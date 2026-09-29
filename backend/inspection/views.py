"""
巡检管理模块 - 视图函数定义

该模块提供了巡检管理相关的API视图，包括：
- 巡检单管理（InspectionViewSet）
- 巡检记录管理（InspectionRecordViewSet）

视图集结构：
    InspectionViewSet
        - 巡检单CRUD操作
        - 审核功能（支持驳回后自动生成报修工单）
    
    InspectionRecordViewSet
        - 巡检记录CRUD操作

审核流程：
    1. 管理员审核巡检单
    2. 通过：更新状态为approved
    3. 驳回：更新状态为rejected，并自动生成报修工单

作者：范广宇
创建日期：2026年
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Case, When, Value, BooleanField
from backend.authentication import get_request_identity
from .models import Inspection, InspectionRecord
from .serializers import InspectionSerializer, InspectionListSerializer, InspectionRecordSerializer


class InspectionViewSet(viewsets.ModelViewSet):
    
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'equipment', 'result']
    search_fields = ['inspection_no', 'staff_name', 'location']

    def get_queryset(self):
        qs = Inspection.objects.all()
        user_type, user_id, identity = get_request_identity(self.request)
        if user_type == 'staff' and user_id:
            qs = qs.filter(staff_id=user_id)
        if getattr(self, 'action', None) == 'list':
            qs = qs.select_related('equipment', 'equipment__equipment_type', 'staff', 'campus', 'building', 'floor').defer(
                'remark', 'review_reply', 'description', 'scene_photo',
            ).annotate(
                has_photo=Case(
                    When(scene_photo='', then=Value(False)),
                    When(scene_photo__isnull=True, then=Value(False)),
                    default=Value(True),
                    output_field=BooleanField(),
                ),
            )
        else:
            qs = qs.select_related('equipment', 'equipment__equipment_type', 'staff', 'campus', 'building', 'floor').prefetch_related('records')
        return qs

    def get_serializer_class(self):
        if getattr(self, 'action', None) == 'list':
            return InspectionListSerializer
        return InspectionSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'staff' and identity:
            data['staff'] = identity.id
            data['staff_no'] = identity.staff_no
            data['staff_name'] = identity.real_name
        equipment_id = data.get('equipment')
        equip = None
        if equipment_id:
            from equipment.models import Equipment
            try:
                equip = Equipment.objects.select_related('room', 'room__floor', 'room__floor__building', 'room__floor__building__campus').get(id=equipment_id)
                if not data.get('equipment_type'):
                    data['equipment_type'] = equip.equipment_type_id
                data['equipment_sequence_number'] = equip.sequence_number
            except Equipment.DoesNotExist:
                return Response({'code': 400, 'message': '所选设备不存在'}, status=status.HTTP_400_BAD_REQUEST)

            if equip.room:
                room_id = data.get('room_id') or data.get('room')
                from location.models import Room
                try:
                    if room_id and str(room_id).isdigit():
                        selected_room = Room.objects.get(id=int(room_id))
                        if equip.room_id != selected_room.id:
                            return Response({
                                'code': 400,
                                'message': f'该设备位于 {equip.room.floor.building.campus.name} {equip.room.floor.building.name} {equip.room.floor.floor_number}层 {equip.room.name}，与所选位置不一致'
                            }, status=status.HTTP_400_BAD_REQUEST)
                except (Room.DoesNotExist, ValueError, TypeError):
                    pass

                if not data.get('campus'):
                    data['campus'] = equip.room.floor.building.campus_id
                if not data.get('building'):
                    data['building'] = equip.room.floor.building_id
                if not data.get('floor'):
                    data['floor'] = equip.room.floor_id
                if not data.get('room_number'):
                    data['room_number'] = equip.room.name

        data.setdefault('status', 'pending')
        
        # 防重复提交检查：1分钟内同一维修人员对同一设备的巡检
        if user_type == 'staff' and identity and equipment_id:
            from django.utils import timezone
            one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
            existing_inspections = Inspection.objects.filter(
                staff_id=identity.id,
                equipment_id=equipment_id,
                created_at__gte=one_minute_ago,
                status='pending'
            )
            if existing_inspections.exists():
                return Response({'code': 400, 'message': '请勿重复提交巡检记录'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        if user_type == 'staff' and identity:
            if not order.staff_no:
                order.staff_no = identity.staff_no
            if not order.staff_name:
                order.staff_name = identity.real_name
            order.save()
        headers = self.get_success_headers(serializer.data)
        return Response({'code': 200, 'message': '提交成功，等待管理员审核', 'data': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除巡检单
        
        请求方式：
            DELETE /api/inspection/list/{id}/
        
        返回格式：
            {'code': 200, 'message': '删除成功'}
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        审核巡检单接口
        
        管理员审核巡检单，支持通过和驳回两种操作。
        驳回时会自动生成报修工单。
        
        请求方式：
            POST /api/inspection/list/{id}/review/
        
        请求参数：
            - review_status: 审核状态（approved/rejected）
            - review_reply: 审核回复
        
        返回格式：
            通过：{'code': 200, 'message': '审核完成'}
            驳回：{'code': 200, 'message': '审核完成，已生成维修工单', 'repair_no': '工单编号'}
        """
        inspection = self.get_object()
        review_status = request.data.get('review_status')
        review_reply = request.data.get('review_reply', '')
        
        # 更新审核状态
        inspection.status = review_status
        inspection.review_reply = review_reply
        inspection.save()
        
        # 驳回时自动生成报修工单
        if review_status == 'rejected':
            from repair.models import RepairOrder
            import random
            import string
            
            def generate_repair_no():
                prefix = 'RP'
                date_str = timezone.now().strftime('%Y%m%d')
                random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                return f"{prefix}{date_str}{random_str}"
            
            order = RepairOrder.objects.create(
                repair_no=generate_repair_no(),
                equipment_name=inspection.equipment.equipment_name if inspection.equipment else '未知设备',
                equipment_type=inspection.equipment.equipment_type if inspection.equipment else None,
                equipment_sequence_number=inspection.equipment_sequence_number,
                location=inspection.location,
                building=inspection.building.name if inspection.building else '',
                floor=str(inspection.floor.floor_number) if inspection.floor else '',
                room=inspection.room_number or '',
                description=f'巡检驳回生成工单。巡检单号：{inspection.inspection_no}。问题描述：{inspection.remark or inspection.description or "无"}。驳回原因：{review_reply}',
                status='WAITING',
                scene_photo=inspection.scene_photo,
                equipment=inspection.equipment
            )
            
            if inspection.campus:
                order.location = inspection.campus.name
                if inspection.building:
                    order.location = f'{inspection.campus.name} {inspection.building.name}'
                if inspection.floor:
                    order.location += f' {inspection.floor.floor_number}层'
                if inspection.room_number:
                    order.location += f' {inspection.room_number}'
            
            # 分配给原巡检人员
            if inspection.staff:
                assigned_staff = inspection.staff
                order.staff_id = assigned_staff.id
                order.staff_no = assigned_staff.staff_no
                order.staff_name = assigned_staff.real_name
                order.status = 'IN_PROGRESS'
                order.accept_time = timezone.now()
            else:
                # 如果没有原巡检人员，查找在线且不忙的维修人员
                online_staffs = RepairOrder.objects.filter(
                    status__in=['IN_PROGRESS', 'PENDING_ADMIN_CLOSE'],
                    is_deleted=False
                ).values_list('staff_id', flat=True).distinct()
                
                from users.models import RepairStaff
                available_staffs = RepairStaff.objects.filter(
                    is_online=True,
                    is_active=True
                ).exclude(id__in=online_staffs).order_by('?')
                
                if available_staffs.exists():
                    assigned_staff = available_staffs.first()
                    order.staff_id = assigned_staff.id
                    order.staff_no = assigned_staff.staff_no
                    order.staff_name = assigned_staff.real_name
                    order.status = 'IN_PROGRESS'
                    order.accept_time = timezone.now()
            
            order.save()
                
            return Response({
                'code': 200,
                'message': '审核完成，已生成维修工单',
                'repair_no': order.repair_no
            })
        
        return Response({
            'code': 200,
            'message': '审核完成'
        })


class InspectionRecordViewSet(viewsets.ModelViewSet):
    """
    巡检记录视图集
    
    提供巡检记录的完整CRUD操作。
    
    继承自ModelViewSet，自动提供CRUD操作。
    """
    
    # 查询集
    queryset = InspectionRecord.objects.all()
    
    # 序列化器
    serializer_class = InspectionRecordSerializer
