"""
报修管理模块 - 视图函数定义

该模块提供了报修管理相关的API视图，是系统的核心业务逻辑层。
包含报修工单管理、评价管理、转派管理、在线状态管理等完整功能。

视图集结构：
    RepairOrderViewSet (报修工单管理)
        - 工单CRUD操作
        - 接单、完成、审核、转派等业务操作
        - 统计和排名功能
    
    TransferRecordViewSet (转派记录)
        - 转派记录查询
    
    StaffOnlineStatusViewSet (在线状态)
        - 心跳检测
        - 状态管理
    
    AttachmentViewSet (附件管理)
        - 附件上传和管理
    
    EvaluationViewSet (评价管理)
        - 评价CRUD操作
        - 统计分析功能
    
    RepairRecordViewSet (维修记录)
        - 维修记录查询和审核
    
    EvaluationAppealViewSet (评价申诉)
        - 申诉创建和处理

认证机制：
    - 支持Django会话认证
    - 支持独立session认证（维修人员、管理员）
    - 支持参数传递认证（staff_id、user_id）

作者：范广宇
创建日期：2026年
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Count, Q, F, Sum
from datetime import timedelta
from collections import defaultdict
import json
from .models import RepairOrder, Evaluation, EvaluationAppeal, TransferRecord, StaffOnlineStatus, Attachment
from equipment.models import Equipment
from location.models import Campus, Building, Floor, Room
from users.models import RepairStaff
from common.models import SparePart, RepairSparePart, SparePartRecord
from .serializers import (RepairOrderSerializer, RepairOrderListSerializer, EvaluationSerializer, EvaluationAppealSerializer,
                          TransferRecordSerializer, StaffOnlineStatusSerializer, AttachmentSerializer)
from backend.authentication import get_request_identity


class RepairOrderViewSet(viewsets.ModelViewSet):
    """
    报修工单视图集
    
    该视图集是系统的核心业务视图，提供报修工单的完整生命周期管理。
    
    继承自ModelViewSet，自动提供CRUD操作：
        - list: 获取工单列表
        - create: 创建工单
        - retrieve: 获取工单详情
        - update: 更新工单
        - partial_update: 部分更新
        - destroy: 删除工单
    
    自定义操作：
        - check_duplicate: 检查重复报修
        - accept: 接单
        - complete: 提交完成
        - review: 审核
        - transfer: 转派
        - soft_delete: 软删除
        - cancel: 取消工单
        - online_staff_list: 在线维修人员列表
        - statistics: 工单统计
        - staff_ranking: 维修人员排名
        - my_orders: 我的工单
        - pending_evaluation: 待评价工单
    
    权限控制：
        - 根据用户类型返回不同的查询集
        - 普通用户只能查看自己的工单
        - 维修人员只能查看分配给自己的工单
        - 管理员可以查看所有工单
    """
    
    # 基础查询集：排除已删除的工单
    queryset = RepairOrder.objects.filter(is_deleted=False)
    
    # 序列化器
    serializer_class = RepairOrderSerializer
    
    # 过滤后端配置
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # 可过滤字段
    filterset_fields = ['status', 'user_type']
    
    # 可搜索字段
    search_fields = ['repair_no', 'equipment_name', 'user_name']
    
    def get_queryset(self):
        """
        根据 Token 身份获取查询集（严格数据隔离）

        - admin: 查全量（支持 staff_id 参数筛选指定维修人员的工单）
        - staff: 只看自己的工单 + 所有待接单工单
        - user: 只看自己的工单
        - 未认证: 返回空集
        """
        user_type, user_id, identity = get_request_identity(self.request)
        qs = RepairOrder.objects.filter(is_deleted=False)

        # 列表接口做“轻量查询”：延迟加载大字段，避免一次性序列化出几十 MB
        if getattr(self, 'action', None) == 'list':
            qs = qs.select_related('equipment', 'equipment_type', 'user', 'staff').prefetch_related('used_parts__spare_part').defer(
                'remark',
                'review_reply',
                'description',
            )
        else:
            qs = qs.select_related('equipment', 'equipment_type', 'user', 'staff').prefetch_related('used_parts__spare_part')

        if user_type == 'admin':
            # 管理员看全量，支持 staff_id 筛选
            staff_id_param = self.request.query_params.get('staff_id')
            if staff_id_param:
                try:
                    return qs.filter(staff_id=int(staff_id_param)).exclude(status__in=['REJECTED'])
                except (ValueError, TypeError):
                    pass
            return qs

        elif user_type == 'staff':
            staff_id = user_id
            status_param = self.request.query_params.get('status')
            if status_param == 'WAITING':
                return qs.filter(status='WAITING')
            elif status_param:
                return qs.filter(staff_id=staff_id, status=status_param).exclude(status__in=['REJECTED'])
            else:
                return qs.filter(
                    Q(staff_id=staff_id) | Q(status='WAITING')
                ).exclude(status__in=['REJECTED'])

        elif user_type == 'user':
            return qs.filter(user_id=user_id)

        # 未认证：返回空集
        return RepairOrder.objects.none()

    def get_serializer_class(self):
        # 列表页用轻量序列化器，详情/创建/更新仍用完整序列化器
        if getattr(self, 'action', None) == 'list':
            return RepairOrderListSerializer
        return RepairOrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        创建报修工单
        
        处理工单创建请求，包括：
        1. 关联当前用户
        2. 处理位置信息（校区、楼栋、楼层）
        3. 验证设备信息
        4. 保存现场照片
        5. 尝试自动派单
        
        请求方式：
            POST /api/repair/orders/
        
        返回格式：
            成功：{'code': 200, 'message': '报修成功', 'data': {工单信息}}
            失败：{'code': 400, 'message': '错误信息'}
        """
        data = request.data.copy()

        # 关联当前用户（从 Token 获取身份）
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'user' and user_id:
            data['user'] = user_id

        # 处理现场照片数据
        scene_photos = data.pop('scene_photos', None)

        # 处理校区信息
        campus_obj = None
        if 'campus' in data and data['campus']:
            campus_id = data.pop('campus')
            try:
                campus_obj = Campus.objects.get(id=campus_id)
                data['location'] = campus_obj.name
            except (Campus.DoesNotExist, ValueError):
                data['location'] = str(campus_id)

        building_obj = None
        if 'building' in data and data['building']:
            building_id = data.get('building')
            try:
                building_obj = Building.objects.get(id=building_id)
                data['building'] = building_obj.name
            except (Building.DoesNotExist, ValueError, TypeError):
                pass

        floor_obj = None
        if 'floor' in data and data['floor']:
            floor_id = data.get('floor')
            try:
                floor_obj = Floor.objects.get(id=floor_id)
                data['floor'] = str(floor_obj.floor_number)
            except (Floor.DoesNotExist, ValueError, TypeError):
                pass

        room_obj = None
        if 'room_id' in data and data['room_id']:
            room_id = data.pop('room_id')
            try:
                room_obj = Room.objects.select_related('floor', 'floor__building', 'floor__building__campus').get(id=room_id)
                data['room'] = room_obj.name
                if not data.get('location') and room_obj.floor.building.campus:
                    data['location'] = room_obj.floor.building.campus.name
                if not data.get('building') and room_obj.floor.building:
                    data['building'] = room_obj.floor.building.name
                if not data.get('floor'):
                    data['floor'] = str(room_obj.floor.floor_number)
            except (Room.DoesNotExist, ValueError, TypeError):
                pass

        # 验证设备：优先使用前端传来的equipment_id（精准关联）
        equipment_id_from_frontend = data.get('equipment_id')
        equip = None

        if equipment_id_from_frontend:
            try:
                equip = Equipment.objects.select_related(
                    'equipment_type', 'room', 'room__floor', 'room__floor__building', 'room__floor__building__campus',
                    'floor', 'floor__building', 'floor__building__campus', 'building', 'building__campus'
                ).get(id=equipment_id_from_frontend)
                data['equipment'] = equip.id
                data['equipment_name'] = equip.equipment_name
                data['equipment_sequence_number'] = equip.sequence_number
                if equip.equipment_type_id:
                    data['equipment_type'] = equip.equipment_type_id
            except Equipment.DoesNotExist:
                return Response({'code': 400, 'message': '所选设备不存在'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            equipment_name = data.get('equipment_name', '')
            equipment_id = data.get('equipment')

            if equipment_name:
                equip_query = Equipment.objects.select_related(
                    'equipment_type', 'room', 'room__floor', 'room__floor__building', 'room__floor__building__campus',
                    'floor', 'floor__building', 'floor__building__campus', 'building', 'building__campus'
                ).filter(equipment_name=equipment_name)

                location_desc = ''
                if room_obj:
                    equip = equip_query.filter(room_id=room_obj.id).first()
                    location_desc = f'{room_obj.floor.building.campus.name} {room_obj.floor.building.name} {room_obj.floor.floor_number}层 {room_obj.name}'
                elif floor_obj:
                    equip = equip_query.filter(floor_id=floor_obj.id).first()
                    location_desc = f'{floor_obj.building.campus.name} {floor_obj.building.name} {floor_obj.floor_number}层'
                elif building_obj:
                    equip = equip_query.filter(building_id=building_obj.id).first()
                    location_desc = f'{building_obj.campus.name} {building_obj.name}'
                elif campus_obj:
                    building_ids = Building.objects.filter(campus_id=campus_obj.id).values_list('id', flat=True)
                    equip = equip_query.filter(building_id__in=building_ids).first()
                    location_desc = f'{campus_obj.name}'

                if not equip:
                    return Response({
                        'code': 400,
                        'message': f'该位置不存在设备【{equipment_name}】，请确认设备位置后重新报修！'
                    }, status=status.HTTP_400_BAD_REQUEST)

                data['equipment'] = equip.id
                data['equipment_name'] = equipment_name
                data['equipment_sequence_number'] = equip.sequence_number
                if equip.equipment_type_id:
                    data['equipment_type'] = equip.equipment_type_id

            elif equipment_id:
                try:
                    equip = Equipment.objects.select_related(
                        'equipment_type', 'room', 'room__floor', 'room__floor__building', 'room__floor__building__campus',
                        'floor', 'floor__building', 'floor__building__campus', 'building', 'building__campus'
                    ).get(id=equipment_id)
                    data['equipment_name'] = equip.equipment_name
                    data['equipment_sequence_number'] = equip.sequence_number
                    if equip.equipment_type_id:
                        data['equipment_type'] = equip.equipment_type_id
                except Equipment.DoesNotExist:
                    return Response({'code': 400, 'message': '所选设备不存在'}, status=status.HTTP_400_BAD_REQUEST)

        # 防重复报修校验（后端强制，不可绕过）
        equipment_name = data.get('equipment_name', '')
        if not equipment_name and equipment_id:
            try:
                equipment_name = Equipment.objects.get(id=equipment_id).equipment_name
            except Equipment.DoesNotExist:
                pass

        if equipment_name:
            location = data.get('location', '')
            building = data.get('building', '')
            floor = data.get('floor', '')
            room = data.get('room', '')

            eq_id = data.get('equipment')
            is_dup, msg, _ = _check_duplicate_repair(equipment_name, location, building, floor, room, equipment_id=eq_id)
            if is_dup:
                return Response({
                    'code': 400,
                    'message': msg
                }, status=status.HTTP_400_BAD_REQUEST)

        # 创建工单
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # 从用户对象中正确设置user_type（模型save中的逻辑因默认值无法生效）
        need_save = False
        if order.user and hasattr(order.user, 'user_type'):
            real_user_type = order.user.user_type
            if real_user_type in ('student', 'teacher') and order.user_type != real_user_type:
                order.user_type = real_user_type
                need_save = True

        # 教师报修自动标记为紧急
        if order.user_type == 'teacher' and not order.is_urgent:
            order.is_urgent = True
            need_save = True

        if need_save:
            order.save(update_fields=['user_type', 'is_urgent'])

        if not order.equipment_name and equipment_name:
            order.equipment_name = equipment_name
            order.save(update_fields=['equipment_name'])

        if not order.equipment_name and order.equipment:
            try:
                order.equipment_name = order.equipment.equipment_name
                order.equipment_type = order.equipment.equipment_type
                order.save(update_fields=['equipment_name', 'equipment_type'])
            except Exception:
                pass

        if order.equipment:
            Equipment.recalculate_fault_count(order.equipment_id)

        # 保存现场照片
        if scene_photos and isinstance(scene_photos, list):
            for i, photo_data in enumerate(scene_photos):
                if not photo_data or not str(photo_data).strip():
                    continue
                # 第一张照片保存到工单的scene_photo字段
                if i == 0 and isinstance(photo_data, str) and photo_data.startswith('data:'):
                    order.scene_photo = photo_data
                    order.save()
                # 创建附件记录
                try:
                    Attachment.objects.create(
                        order=order,
                        uploader=request.user if request.user.is_authenticated else None,
                        file_name=f'报修照片_{order.id}',
                        file_path=str(photo_data),
                        file_size=0,
                        file_type='image'
                    )
                except Exception:
                    pass
        
        # 尝试自动派单
        try:
            auto_assign_order(order)
        except Exception as e:
            pass
        
        # 重新序列化更新后的订单，确保is_urgent字段正确返回
        serializer = self.get_serializer(order)
        
        return Response({
            'code': 200,
            'message': '报修成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='check_duplicate')
    def check_duplicate(self, request):
        equipment_name = request.data.get('equipment_name', '')
        location = request.data.get('location', '')
        building = request.data.get('building', '')
        floor = request.data.get('floor', '')
        room = request.data.get('room', '')

        if not equipment_name:
            return Response({'is_duplicate': False})

        is_dup, msg, count = _check_duplicate_repair(equipment_name, location, building, floor, room)
        if is_dup:
            return Response({
                'is_duplicate': True,
                'message': msg,
                'count': count
            })

        return Response({'is_duplicate': False})
    
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        """
        接单接口（带并发锁）
        
        维修人员接受工单，工单状态变为"维修中"。
        使用数据库事务 + select_for_update() 原子锁，保证同一工单仅一人可接单。
        
        请求方式：
            POST /api/repair/orders/{id}/accept/
        
        前置条件：
            - 工单状态为"待接单"
            - 请求者为维修人员
        
        返回格式：
            成功：{'code': 200, 'message': '接单成功'}
            并发冲突：{'code': 400, 'message': '当前工单已被其他维修人员接单！'}
            失败：{'code': 400/403, 'message': '错误信息'}
        """
        user_type, user_id, identity = get_request_identity(request)
        if user_type != 'staff' or not identity:
            return Response({'code': 403, 'message': '无权限操作，请确认维修员身份'}, status=status.HTTP_403_FORBIDDEN)
        staff = identity

        if not getattr(staff, 'is_online', False):
            return Response({'code': 400, 'message': '当前账号未上线，暂无法接单，请先完成上线操作后再尝试'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 使用select_for_update锁定工单记录，防止并发接单
                order = RepairOrder.objects.select_for_update().get(pk=pk)
                
                # 再次检查工单状态（可能在获取锁之前已被其他人接单）
                if order.status != 'WAITING':
                    if order.status == 'IN_PROGRESS':
                        return Response({
                            'code': 400,
                            'message': f'当前工单已被其他维修员接单！（当前维修员：{order.staff_name or "未知"}）'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    return Response({'code': 400, 'message': '当前状态无法接单'}, status=status.HTTP_400_BAD_REQUEST)

                # 更新工单信息
                order.status = 'IN_PROGRESS'
                order.staff_id = staff.id
                order.staff_no = staff.staff_no
                order.staff_name = staff.real_name
                order.accept_time = timezone.now()
                order.repair_start_time = timezone.now()
                order.save()

            return Response({'code': 200, 'message': '接单成功'})
            
        except RepairOrder.DoesNotExist:
            return Response({'code': 404, 'message': '工单不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        提交完成接口
        
        维修人员完成维修后提交，工单状态变为"待管理员审核"。
        支持备件扣减、现场照片上传等功能。
        
        请求方式：
            POST /api/repair/orders/{id}/complete/
        
        请求参数：
            - remark: 备注说明
            - scene_photo: 现场照片（支持多张）
            - spare_parts: 使用的备件列表
        
        返回格式：
            成功：{'code': 200, 'message': '提交成功，等待管理员审核'}
            失败：{'code': 400/404/500, 'message': '错误信息'}
        """
        try:
            order = self.get_object()
        except Exception as e:
            return Response({'code': 404, 'message': '工单不存在'}, status=404)
        
        # 检查工单状态
        if order.status != 'IN_PROGRESS':
            return Response({'code': 400, 'message': '当前状态无法提交完成'}, status=status.HTTP_400_BAD_REQUEST)

        # 获取请求参数
        remark = request.data.get('remark', '')
        scene_photos = []

        # ✅ 修正1：优先接收 scene_photos（前端发送的正确字段名）
        raw_photos_list = request.data.get('scene_photos')
        if raw_photos_list:
            if isinstance(raw_photos_list, list):
                scene_photos.extend(raw_photos_list)
            elif isinstance(raw_photos_list, str):
                scene_photos.append(raw_photos_list)

        # ✅ 修正2：兼容接收 scene_photo[]（某些前端库格式）
        try:
            raw_photos_array = request.data.getlist('scene_photo[]') or []
            scene_photos.extend(raw_photos_array)
        except Exception:
            pass

        # ✅ 修正3：兼容接收 scene_photo（单张）
        scene_photo_single = request.data.get('scene_photo')
        if scene_photo_single:
            if isinstance(scene_photo_single, list):
                scene_photos.extend(scene_photo_single)
            else:
                scene_photos.append(scene_photo_single)

        spare_parts_data = request.data.get('spare_parts', [])
        if isinstance(spare_parts_data, str):
            try:
                spare_parts_data = json.loads(spare_parts_data)
            except (json.JSONDecodeError, TypeError):
                spare_parts_data = []

        if spare_parts_data:
            try:
                with transaction.atomic():
                    for item in spare_parts_data:
                        sp_id = item.get('id') if isinstance(item, dict) else None
                        quantity = int(item.get('quantity', 1)) if isinstance(item, dict) else 1
                        if not sp_id or quantity < 1:
                            continue
                        
                        # 使用select_for_update锁定记录
                        part = SparePart.objects.select_for_update().filter(id=sp_id).first()
                        if not part:
                            raise ValueError(f'备件ID {sp_id} 不存在')
                        
                        before_qty = part.quantity
                        if quantity > before_qty:
                            raise ValueError(f'备件「{part.name}」库存不足，需要{quantity}，当前库存{before_qty}')
                        
                        # 扣减库存
                        part.quantity = F('quantity') - quantity
                        part.save(update_fields=['quantity'])
                        part.refresh_from_db()
                        
                        # 创建维修备件记录
                        RepairSparePart.objects.create(
                            repair_order=order,
                            spare_part=part,
                            quantity=quantity,
                            unit_price=getattr(part, 'unit_price') or 0
                        )
                        
                        # 创建备件出入库记录
                        SparePartRecord.objects.create(
                            part=part,
                            record_type='out',
                            quantity=quantity,
                            before_quantity=before_qty,
                            after_quantity=part.quantity,
                            operator=str(order.staff_name or ''),
                            remark=f'工单{order.repair_no}维修使用'
                        )
            except ValueError as ve:
                return Response({'code': 400, 'message': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'code': 500, 'message': f'备件扣减失败: {str(e)}'}, status=500)

        # 更新工单状态
        order.status = 'PENDING_ADMIN_CLOSE'
        order.repair_end_time = timezone.now()
        order.complete_time = timezone.now()
        order.remark = remark or ''

        # 计算实际耗时
        start_time = order.repair_start_time or order.accept_time
        if start_time and order.repair_end_time:
            delta = order.repair_end_time - start_time
            order.actual_duration = int(delta.total_seconds() / 60)

        try:
            order.save()
        except Exception as e:
            return Response({'code': 500, 'message': f'保存工单失败: {str(e)}'}, status=500)

        # 保存维修完成照片到Attachment表
        for i, photo in enumerate(scene_photos):
            if not photo or not str(photo).strip():
                continue
            try:
                Attachment.objects.create(
                    order=order,
                    file_name=f'维修照片_{order.id}_{i+1}',
                    file_path=str(photo),
                    file_size=0,
                    file_type='image'
                )
            except Exception:
                pass

        return Response({'code': 200, 'message': '提交成功，等待管理员审核'})
    
    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, pk=None):
        """
        审核接口
        
        管理员审核工单，可以批准或驳回。
        批准后工单状态变为"已完成"，驳回后状态变为"维修中"。
        
        请求方式：
            POST /api/repair/orders/{id}/review/
        
        请求参数：
            - review_status: 审核状态（approved/rejected）
            - review_reply: 审核回复
        
        返回格式：
            成功：{'code': 200, 'message': '审核成功'}
            失败：{'code': 400, 'message': '错误信息'}
        """
        # 检查是否为管理员
        user_type, user_id, identity = get_request_identity(request)
        if user_type != 'admin':
            return Response({'code': 403, 'message': '仅管理员可审核工单'}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        
        # 检查工单状态
        if order.status != 'PENDING_ADMIN_CLOSE':
            return Response({'code': 400, 'message': '当前状态无法审核'}, status=status.HTTP_400_BAD_REQUEST)
        
        review_status = request.data.get('review_status')
        review_reply = request.data.get('review_reply', '')
        
        # 更新工单状态
        if review_status == 'approved':
            # 审核通过
            order.status = 'CLOSED'
        elif review_status == 'rejected':
            order.status = 'IN_PROGRESS'
        else:
            return Response({'code': 400, 'message': '无效的审核状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_type == 'user':
            order.reviewer = identity
        else:
            order.reviewer = None
        order.review_reply = review_reply
        order.review_time = timezone.now()
        order.save()

        if order.equipment_id:
            Equipment.recalculate_fault_count(order.equipment_id)
        
        return Response({'code': 200, 'message': '审核成功'})
    
    @action(detail=True, methods=['post'], url_path='transfer')
    def transfer(self, request, pk=None):
        """
        转派接口

        将工单转派给其他维修人员。
        转派继承当前工单状态，仅更换维修人员。

        请求方式：
            POST /api/repair/orders/{id}/transfer/

        请求参数：
            - to_staff/staff_id: 目标维修人员ID（必需）
            - reason: 转派原因

        返回格式：
            成功：{'code': 200, 'message': '转派成功'}
            失败：{'code': 400/404, 'message': '错误信息'}
        """
        order = self.get_object()

        user_type, user_id, identity = get_request_identity(request)
        is_admin = user_type == 'admin'

        # 检查工单状态
        if order.status not in ['WAITING', 'IN_PROGRESS']:
            return Response({'code': 400, 'message': '只有待接单或处理中的工单才能转派'}, status=status.HTTP_400_BAD_REQUEST)

        # 维修人员转派限制
        if not is_admin:
            if order.status != 'IN_PROGRESS':
                return Response({'code': 400, 'message': '维修员只能转让处理中的工单'}, status=status.HTTP_400_BAD_REQUEST)
            # 接单超过3分钟不能转让
            if order.accept_time:
                time_diff = timezone.now() - order.accept_time
                if time_diff.total_seconds() > 180:
                    return Response({'code': 400, 'message': '接单已超过3分钟，无法转让'}, status=status.HTTP_400_BAD_REQUEST)

        to_staff_id = request.data.get('to_staff') or request.data.get('staff_id')
        reason = request.data.get('reason', '')

        from_staff_id = order.staff_id
        from_staff_name = order.staff_name

        if not is_admin:
            order.staff_id = None
            order.staff_no = None
            order.staff_name = None
            order.status = 'WAITING'
            order.accept_time = None
            order.repair_start_time = None
            order.is_transferred = True
            
            TransferRecord.objects.create(
                order=order,
                from_staff_id=from_staff_id,
                to_staff=None,
                transfer_type='staff_return',
                reason=reason,
                status='approved',
                effective_time=timezone.now()
            )
            order.save()
            
            return Response({
                'code': 200,
                'message': '转派成功，工单已回流至待接单池'
            })
        # 管理员转派：转派给指定维修人员
        else:
            if not to_staff_id or str(to_staff_id) in ('0', '', 'None', 'null'):
                return Response({'code': 400, 'message': '请选择目标维修员'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                to_staff = RepairStaff.objects.get(id=to_staff_id)
            except RepairStaff.DoesNotExist:
                return Response({'code': 404, 'message': '目标维修员不存在'}, status=status.HTTP_404_NOT_FOUND)

            # 转派给指定维修人员（继承当前状态，仅换人）
            order.staff_id = to_staff.id
            order.staff_no = to_staff.staff_no
            order.staff_name = to_staff.real_name
            if order.status == 'WAITING':
                order.status = 'IN_PROGRESS'
                order.accept_time = timezone.now()
                order.repair_start_time = timezone.now()

            TransferRecord.objects.create(
                order=order,
                from_staff_id=from_staff_id,
                to_staff=to_staff,
                transfer_type='admin',
                reason=reason,
                status='approved',
                effective_time=timezone.now()
            )
            order.save()

            return Response({
                'code': 200,
                'message': '转派成功'
            })
    
    @action(detail=True, methods=['delete'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        """
        软删除接口
        
        将工单标记为已删除，不实际删除数据。
        
        请求方式：
            DELETE /api/repair/orders/{id}/soft-delete/
        
        返回格式：
            成功：{'code': 200, 'message': '删除成功'}
        """
        order = self.get_object()
        order.is_deleted = True
        order.deleted_at = timezone.now()
        order.status = 'CANCELLED' if order.status == 'WAITING' else order.status
        order.save()

        return Response({'code': 200, 'message': '删除成功'})

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        取消工单接口

        用户取消待接单状态的工单，管理员可以取消任何非已完成状态的工单。

        请求方式：
            POST /api/repair/orders/{id}/cancel/

        返回格式：
            成功：{'code': 200, 'message': '取消成功'}
            失败：{'code': 400/404, 'message': '错误信息'}
        """
        try:
            order = self.get_object()
        except Exception:
            return Response({'code': 404, 'message': '工单不存在'}, status=404)

        # 检查是否为管理员（从 Token 获取身份）
        user_type, user_id, identity = get_request_identity(request)
        is_admin = user_type == 'admin'

        if is_admin:
            # 管理员可以取消任何非已完成的工单
            if order.status == 'CLOSED':
                return Response({'code': 400, 'message': '已完成的工单不能取消'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 普通用户只能取消待接单状态的工单
            if order.status not in ['WAITING']:
                return Response({'code': 400, 'message': '工单已接受，不可取消，如果想取消，请联系管理员！'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'REJECTED'
        order.is_deleted = True
        order.deleted_at = timezone.now()
        order.save()

        if order.equipment_id:
            Equipment.recalculate_fault_count(order.equipment_id)

        return Response({'code': 200, 'message': '取消成功'})

    @action(detail=False, methods=['get'], url_path='online-staff-list')
    def online_staff_list(self, request):
        """
        获取在线维修人员列表
        
        返回当前在线的维修人员信息，用于派单选择。
        
        请求方式：
            GET /api/repair/orders/online-staff-list/
        
        返回格式：
            {'results': [{维修人员信息}]}
        """
        online_status_ids = StaffOnlineStatus.objects.filter(
            is_online=True
        ).values_list('staff_id', flat=True)
        
        staffs = RepairStaff.objects.filter(id__in=online_status_ids)[:50]
        result = []
        for s in staffs:
            result.append({
                'id': s.id,
                'real_name': s.real_name,
                'staff_no': s.staff_no,
                'is_online': True
            })
        
        if not result:
            all_online = RepairStaff.objects.filter(status='online')[:20]
            for s in all_online:
                result.append({
                    'id': s.id,
                    'real_name': s.real_name,
                    'staff_no': s.staff_no,
                    'is_online': True
                })
        
        return Response({'results': result})

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        from django.core.cache import cache

        user_type, user_id, identity = get_request_identity(request)

        if user_type == 'staff' and user_id:
            cache_key = f'staff_stats_{user_id}'
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)

            my_orders = RepairOrder.objects.filter(is_deleted=False, staff_id=user_id)
            all_available = RepairOrder.objects.filter(is_deleted=False, status='WAITING')
            total = my_orders.count() + all_available.count()
            waiting = all_available.count()
            in_progress = my_orders.filter(status='IN_PROGRESS').count()
            pending_review = my_orders.filter(status='PENDING_ADMIN_CLOSE').count()
            completed = my_orders.filter(status='CLOSED').count()

            result = {
                'total': total,
                'pending': waiting,
                'accepted': in_progress,
                'repairing': pending_review,
                'completed': completed
            }

            today = timezone.now().date()
            today_orders = my_orders.filter(
                status='CLOSED',
                complete_time__date=today
            )
            result['today_completed'] = today_orders.count()

            duration_result = today_orders.aggregate(total=Sum('actual_duration'))
            result['today_duration'] = duration_result['total'] or 0

            today_evaluations = Evaluation.objects.filter(
                staff_id=user_id,
                is_deleted=False,
                created_at__date=today
            )
            avg_result = today_evaluations.aggregate(avg=Avg('rating'))
            result['today_avg_rating'] = round(avg_result['avg'], 1) if avg_result['avg'] else 0

            cache.set(cache_key, result, 30)
            return Response(result)

        elif user_type == 'user' and user_id:
            cache_key = f'user_stats_{user_id}'
            cached = cache.get(cache_key)
            if cached:
                return Response(cached)

            base_qs = RepairOrder.objects.filter(is_deleted=False, user_id=user_id)
            status_agg = base_qs.values('status').annotate(cnt=Count('id'))
            status_map = {item['status']: item['cnt'] for item in status_agg}
            total = sum(status_map.values())
            result = {
                'total': total,
                'pending': status_map.get('WAITING', 0),
                'accepted': status_map.get('IN_PROGRESS', 0),
                'repairing': status_map.get('PENDING_ADMIN_CLOSE', 0),
                'completed': status_map.get('CLOSED', 0)
            }
            cache.set(cache_key, result, 30)
            return Response(result)

        # admin 统计：带缓存
        trend_days = int(request.query_params.get('trend_days', 30))
        cache_key = f'admin_stats_{trend_days}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        base_qs = RepairOrder.objects.filter(is_deleted=False)

        # 合并6次count为1条SQL
        status_agg = base_qs.values('status').annotate(cnt=Count('id'))
        status_map = {item['status']: item['cnt'] for item in status_agg}
        waiting = status_map.get('WAITING', 0)
        in_progress = status_map.get('IN_PROGRESS', 0)
        pending_review = status_map.get('PENDING_ADMIN_CLOSE', 0)
        completed = status_map.get('CLOSED', 0)
        rejected_count = status_map.get('REJECTED', 0)
        total = sum(status_map.values())

        result = {
            'total': total,
            'pending': waiting,
            'accepted': in_progress,
            'repairing': pending_review,
            'completed': completed
        }

        completed_orders = base_qs.filter(status='CLOSED', actual_duration__isnull=False)
        dur_agg = completed_orders.aggregate(total=Sum('actual_duration'), cnt=Count('id'))
        result['avg_duration'] = round((dur_agg['total'] or 0) / dur_agg['cnt'] / 60, 1) if dur_agg['cnt'] else 0
        result['completion_rate'] = round(completed / total * 100, 1) if total else 0
        result['urgent_orders'] = base_qs.filter(user_type='teacher').exclude(status__in=['CLOSED', 'REJECTED']).count()

        eval_qs = Evaluation.objects.filter(is_deleted=False)
        eval_avg = eval_qs.aggregate(avg=Avg('rating'))['avg'] or 0
        result['avg_rating'] = round(eval_avg, 1)

        # 趋势：用数据库 TruncDate 替代 Python 遍历
        since_date = timezone.now().date() - timedelta(days=trend_days - 1)
        since_dt = timezone.datetime.combine(since_date, timezone.datetime.min.time())

        from django.db.models.functions import TruncDate
        trend_total = (
            base_qs.filter(created_at__gte=since_dt)
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(cnt=Count('id'))
        )
        trend_total_map = {item['date']: item['cnt'] for item in trend_total}

        trend_completed = (
            base_qs.filter(created_at__gte=since_dt, status='CLOSED')
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(cnt=Count('id'))
        )
        trend_completed_map = {item['date']: item['cnt'] for item in trend_completed}

        date_list = []
        for i in range(trend_days):
            d = (timezone.now().date() - timedelta(days=trend_days - 1 - i))
            date_list.append({
                'date': d.strftime('%m-%d'),
                'total': trend_total_map.get(d, 0),
                'completed': trend_completed_map.get(d, 0)
            })
        result['trend'] = date_list

        hot_qs = base_qs.values('equipment_name').annotate(cnt=Count('id')).order_by('-cnt')[:10]
        result['hot_equipments'] = [{'equipment_name': e['equipment_name'] or '未知', 'repair_count': e['cnt']} for e in hot_qs]

        valid_campus_names = list(Campus.objects.values_list('name', flat=True).order_by('sort_order', 'id'))
        campus_data = {}
        for loc, cnt in base_qs.values_list('location').annotate(cnt=Count('id')):
            if loc in valid_campus_names:
                campus_data[loc] = (campus_data.get(loc, 0) or 0) + (cnt or 0)
        ordered_campus = {name: campus_data.get(name, 0) for name in valid_campus_names}
        result['campus_distribution'] = ordered_campus

        staff_completed = base_qs.filter(status='CLOSED').values('staff_name').annotate(cnt=Count('id')).order_by('-cnt')[:10]
        result['staff_completed'] = [{'name': s['staff_name'] or '未分配', 'count': s['cnt']} for s in staff_completed]

        urgent_list = base_qs.filter(user_type='teacher').exclude(status__in=['CLOSED', 'REJECTED']).order_by('-created_at')[:10]
        result['urgent_orders_list'] = [
            {'id': o.id, 'repair_no': o.repair_no, 'equipment_name': o.equipment_name,
             'status': o.status, 'created_at': o.created_at.isoformat() if o.created_at else None,
             'user_name': o.user_name, 'location': o.location}
            for o in urgent_list
        ]

        cache.set(cache_key, result, 60)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='staff-ranking')
    def staff_ranking(self, request):
        """
        维修人员排名接口
        
        返回完成工单数最多的维修人员排名。
        
        请求方式：
            GET /api/repair/orders/staff-ranking/
        
        返回格式：
            {'results': [{排名信息}]}
        """
        ranking = RepairStaff.objects.annotate(
            completed_count=Count(
                'repair_orders',
                filter=Q(repair_orders__status='CLOSED', repair_orders__is_deleted=False)
            )
        ).filter(completed_count__gt=0).order_by('-completed_count')[:10]

        result = []
        for s in ranking:
            # 计算平均评分
            avg_rating = Evaluation.objects.filter(
                staff_id=s.id, is_deleted=False
            ).aggregate(avg=Avg('rating'))['avg'] or 0
            result.append({
                'id': s.id,
                'real_name': s.real_name,
                'staff_no': s.staff_no,
                'completed_count': s.completed_count,
                'avg_rating': round(float(avg_rating), 1)
            })
        
        return Response({'results': result})
    
    @action(detail=False, methods=['get'], url_path='my-orders')
    def my_orders(self, request):
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'user' and user_id:
            orders = self.get_queryset().filter(user_id=user_id)[:20]
        elif user_type == 'staff' and user_id:
            orders = self.get_queryset().filter(staff_id=user_id)[:20]
        else:
            orders = self.get_queryset().none()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='pending_evaluation')
    def pending_evaluation(self, request):
        user_type, user_id, identity = get_request_identity(request)
        if user_type != 'user' or not user_id:
            return Response({'results': []})
        
        evaluated_order_ids = Evaluation.objects.filter(
            is_deleted=False, is_hidden=False
        ).filter(
            Q(user_id=user_id) | Q(order__user_id=user_id)
        ).values_list('order_id', flat=True)
        
        orders = self.get_queryset().filter(
            status='CLOSED'
        ).exclude(id__in=evaluated_order_ids)[:20]
        
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


def _check_duplicate_repair(equipment_name, location, building, floor, room, equipment_id=None):
    time_threshold = timezone.now() - timedelta(hours=24)
    dup_q = Q(is_deleted=False, created_at__gte=time_threshold)
    dup_q &= Q(equipment_name=equipment_name)
    dup_q &= Q(location=location)
    dup_q &= Q(building=building)
    dup_q &= Q(floor=floor)
    dup_q &= Q(room=room)
    if equipment_id:
        dup_q &= Q(equipment_id=equipment_id)

    recent_orders = RepairOrder.objects.filter(dup_q)
    has_unfinished = recent_orders.exclude(status__in=['CLOSED', 'REJECTED']).exists()

    if has_unfinished:
        location_str = f'{location} {building} {floor} {room}'.strip()
        return True, f'该{equipment_name}及{location_str}已有未完成的报修工单，请勿重复提交！', recent_orders.count()
    return False, '', 0


def auto_assign_order(order):
    """
    自动派单函数
    
    根据规则自动将工单分配给合适的维修人员。
    当前为空实现，可根据实际需求添加派单逻辑。
    
    参数：
        order: RepairOrder实例
    """
    pass


class TransferRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    转派记录视图集
    
    提供转派记录的只读查询功能。
    
    继承自ReadOnlyModelViewSet，只提供：
        - list: 获取转派记录列表
        - retrieve: 获取转派记录详情
    """
    
    queryset = TransferRecord.objects.all()
    serializer_class = TransferRecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'status', 'transfer_type']


class StaffOnlineStatusViewSet(viewsets.ModelViewSet):
    """
    维修人员在线状态视图集
    
    管理维修人员的在线状态，支持心跳检测机制。
    
    自定义操作：
        - heartbeat: 心跳检测
        - logout: 登出
        - set_status: 设置状态
    """
    
    queryset = StaffOnlineStatus.objects.all()
    serializer_class = StaffOnlineStatusSerializer

    @action(detail=False, methods=['post'], url_path='heartbeat')
    def heartbeat(self, request):
        """
        心跳检测接口
        
        维修人员定期发送心跳请求，更新在线状态。
        
        请求方式：
            POST /api/repair/staff-online/heartbeat/
        
        返回格式：
            成功：{'code': 200, 'message': 'ok'}
            失败：{'code': 403, 'message': 'no permission'}
        """
        user_type, user_id, identity = get_request_identity(request)
        if user_type != 'staff' or not identity:
            return Response({'code': 403, 'message': 'no permission'}, status=403)
        staff = identity

        # 更新或创建在线状态记录
        status_obj, created = StaffOnlineStatus.objects.update_or_create(
            staff_id=staff.id,
            defaults={'is_online': True, 'last_heartbeat': timezone.now(), 'login_time': timezone.now() if created else None}
        )
        
        # 更新维修人员状态
        staff.is_online = True
        staff.status = 'online'
        staff.save()
        
        return Response({'code': 200, 'message': 'ok'})

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        """
        登出接口
        
        维修人员登出时更新在线状态。
        
        请求方式：
            POST /api/repair/staff-online/logout/
        
        返回格式：
            成功：{'code': 200, 'message': 'ok'}
            失败：{'code': 403, 'message': 'no permission'}
        """
        user_type, user_id, identity = get_request_identity(request)
        if user_type != 'staff' or not identity:
            return Response({'code': 403, 'message': 'no permission'}, status=403)

        # 更新在线状态
        StaffOnlineStatus.objects.filter(staff_id=identity.id).update(is_online=False, logout_time=timezone.now())

        # 更新维修人员状态
        identity.is_online = False
        identity.status = 'offline'
        identity.save()

        return Response({'code': 200, 'message': 'ok'})

    @action(detail=False, methods=['post'], url_path='set_status')
    def set_status(self, request):
        """
        设置状态接口
        
        设置维修人员的在岗状态（在线/离线/调休）。
        
        请求方式：
            POST /api/repair/staff-online/set_status/
        
        请求参数：
            - staff_id: 维修人员ID
            - status: 状态（online/offline/leave）
        
        返回格式：
            成功：{'code': 200, 'message': 'done'}
            失败：{'code': 400/404, 'message': '错误信息'}
        """
        target_id = request.data.get('staff_id')
        new_status = request.data.get('status')
        
        if not target_id or new_status not in ['online', 'offline', 'leave']:
            return Response({'code': 400, 'message': 'bad params'}, status=400)
        
        try:
            target = RepairStaff.objects.get(id=target_id)
        except RepairStaff.DoesNotExist:
            return Response({'code': 404, 'message': 'not found'}, status=404)
        
        # 更新维修人员状态
        target.status = new_status
        target.is_online = (new_status == 'online')
        target.save()
        
        # 更新在线状态记录
        StaffOnlineStatus.objects.filter(staff_id=target.id).update(
            is_online=(new_status == 'online'),
            logout_time=timezone.now() if new_status != 'online' else None
        )
        
        return Response({'code': 200, 'message': 'done'})


class AttachmentViewSet(viewsets.ModelViewSet):
    """
    附件视图集
    
    提供附件的上传和管理功能。
    """
    
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order', 'file_type']


class EvaluationViewSet(viewsets.ModelViewSet):
    """
    评价视图集
    
    提供评价的完整管理功能，包括统计分析。
    
    自定义操作：
        - statistics: 评价统计
        - check_evaluated: 检查已评价工单
        - staff_ranking: 维修人员评分排名
        - monthly_trend: 月度趋势
        - dimension_analysis: 维度分析
        - bad_reviews: 差评列表
        - hide: 隐藏评价
        - show: 显示评价
        - admin_review: 管理员审核
    """
    
    queryset = Evaluation.objects.filter(is_deleted=False)
    serializer_class = EvaluationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['rating', 'staff']
    search_fields = ['repair_no', 'user_name', 'staff_name']

    def get_queryset(self):
        qs = Evaluation.objects.filter(is_deleted=False)
        user_type, user_id, identity = get_request_identity(self.request)

        if user_type == 'staff':
            qs = qs.filter(staff_id=user_id)
        elif user_type == 'user':
            qs = qs.filter(Q(user_id=user_id) | Q(order__user_id=user_id))

        month = self.request.query_params.get('month')
        if month:
            try:
                year = int(month[:4])
                month_num = int(month[5:7])
                qs = qs.filter(
                    created_at__year=year,
                    created_at__month=month_num
                )
            except (ValueError, IndexError):
                pass

        return qs

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'user' and user_id:
            data['user'] = user_id

        repair_order_id = data.get('repair_order') or data.get('order')
        if repair_order_id:
            try:
                order = RepairOrder.objects.get(id=repair_order_id)
                data['staff'] = order.staff_id
                data['staff_name'] = str(order.staff_name) or ''
                if not data.get('user') and order.user_id:
                    data['user'] = order.user_id
                if order.user:
                    data['user_name'] = getattr(order.user, 'real_name', '') or str(order.user.username)
                else:
                    data['user_name'] = ''

                quality = int(data.get('quality_rating', 5))
                speed = int(data.get('speed_rating', 5))
                attitude = int(data.get('attitude_rating', 5))
                data['rating'] = round((quality + speed + attitude) / 3)

                existing_eval = Evaluation.objects.filter(
                    order_id=order.id, is_hidden=True, is_deleted=False
                ).first()
                if existing_eval:
                    existing_eval.quality_rating = quality
                    existing_eval.speed_rating = speed
                    existing_eval.attitude_rating = attitude
                    existing_eval.rating = data['rating']
                    existing_eval.content = data.get('content', '')
                    existing_eval.is_hidden = False
                    existing_eval.hidden_reason = ''
                    existing_eval.user_id = data.get('user')
                    existing_eval.user_name = data.get('user_name', '')
                    existing_eval.staff_id = order.staff_id
                    existing_eval.staff_name = str(order.staff_name) or ''
                    existing_eval.save()
                    serializer = self.get_serializer(existing_eval)
                    return Response({'code': 200, 'message': '重新评价成功', 'data': serializer.data})
            except (RepairOrder.DoesNotExist, ValueError, TypeError, AttributeError):
                pass

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if data.get('user'):
            instance.user_id = data['user']
        if data.get('user_name'):
            instance.user_name = data['user_name']
        if data.get('staff'):
            instance.staff_id = data['staff']
        if data.get('staff_name'):
            instance.staff_name = data['staff_name']
        instance.save()
        
        return Response({'code': 200, 'message': '评价成功', 'data': self.get_serializer(instance).data}, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        软删除评价
        
        将评价标记为已删除，不实际删除数据。
        """
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({'code': 200, 'message': '删除成功'})
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        评价统计接口

        - 维修人员：只返回自己的评价统计
        - 管理员：返回所有评价统计（支持 staff_id 参数筛选指定维修人员）
        - 用户：返回自己的评价统计
        """
        qs = Evaluation.objects.filter(is_deleted=False)
        user_type, user_id, identity = get_request_identity(request)

        # 管理员支持 staff_id 参数筛选
        staff_id_param = request.query_params.get('staff_id')
        if user_type == 'admin' and staff_id_param:
            try:
                qs = qs.filter(staff_id=int(staff_id_param))
                pending_appeal = EvaluationAppeal.objects.filter(
                    staff_id=int(staff_id_param), status='pending'
                ).count()
                total = qs.count()
                avg_rating = qs.aggregate(avg=Avg('rating'))['avg'] or 0
                return Response({
                    'total_count': total,
                    'avg_rating': round(avg_rating, 1),
                    'pending_appeal': pending_appeal
                })
            except (ValueError, TypeError):
                pass

        if user_type == 'staff':
            qs = qs.filter(staff_id=user_id)

        # 计算统计数据
        total = qs.count()
        avg_rating = qs.aggregate(avg=Avg('rating'))['avg'] or 0

        # 维修人员计算待处理申诉数
        pending_appeal = 0
        if user_type == 'staff':
            pending_appeal = EvaluationAppeal.objects.filter(
                staff_id=user_id, status='pending'
            ).count()

        return Response({
            'total_count': total,
            'avg_rating': round(avg_rating, 1),
            'pending_appeal': pending_appeal
        })
    
    @action(detail=False, methods=['get'], url_path='check_evaluated')
    def check_evaluated(self, request):
        """
        检查已评价工单接口
        
        检查指定工单是否已被评价。
        
        请求参数：
            - order_ids: 工单ID列表（逗号分隔）
        """
        raw_ids = request.query_params.get('order_ids', '')
        order_ids = [oid for oid in raw_ids.split(',') if oid.strip().isdigit()]
        
        if not order_ids:
            return Response({'evaluated_order_ids': []})
        
        evaluated = Evaluation.objects.filter(
            is_deleted=False,
            order_id__in=order_ids
        ).values_list('order_id', flat=True).distinct()
        
        return Response({'evaluated_order_ids': list(evaluated)})
    
    @action(detail=False, methods=['get'], url_path='staff_ranking')
    def staff_ranking(self, request):
        staffs = RepairStaff.objects.filter(is_active=True)
        ranking = []
        for s in staffs:
            evals = Evaluation.objects.filter(is_deleted=False, staff_id=s.id)
            total = evals.count()
            avg_rating = evals.aggregate(avg=Avg('rating'))['avg'] or 0
            avg_quality = evals.aggregate(avg=Avg('quality_rating'))['avg'] or 0
            avg_speed = evals.aggregate(avg=Avg('speed_rating'))['avg'] or 0
            avg_attitude = evals.aggregate(avg=Avg('attitude_rating'))['avg'] or 0
            completed = RepairOrder.objects.filter(
                staff_id=s.id, status='CLOSED', is_deleted=False
            ).count()
            if total > 0:
                ranking.append({
                    'id': s.id,
                    'staff_name': s.real_name,
                    'staff_no': s.staff_no,
                    'total_evaluations': total,
                    'avg_rating': round(float(avg_rating), 1),
                    'avg_quality': round(float(avg_quality), 1),
                    'avg_speed': round(float(avg_speed), 1),
                    'avg_attitude': round(float(avg_attitude), 1),
                    'completed_orders': completed
                })
        ranking.sort(key=lambda x: x['avg_rating'], reverse=True)
        return Response(ranking[:10])
    
    @action(detail=False, methods=['get'], url_path='monthly_trend')
    def monthly_trend(self, request):
        """
        月度趋势接口
        
        返回近6个月的评价趋势数据。
        """
        since = timezone.now() - timedelta(days=180)
        evals = Evaluation.objects.filter(
            is_deleted=False,
            created_at__isnull=False,
            created_at__gte=since
        ).values_list('created_at', 'rating')
        
        monthly = defaultdict(lambda: {'count': 0, 'total_rating': 0})
        for dt, rating in evals:
            if dt:
                key = dt.strftime('%Y-%m')
                monthly[key]['count'] += 1
                if rating:
                    monthly[key]['total_rating'] += rating
        
        result = [
            {'month': k, 'count': v['count'],
             'avg_rating': round(v['total_rating'] / v['count'], 1) if v['count'] else 0}
            for k, v in sorted(monthly.items())
        ]
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='dimension_analysis')
    def dimension_analysis(self, request):
        """
        维度分析接口
        
        返回各评分维度的分布数据。
        """
        result = {}
        for field in ['quality_rating', 'speed_rating', 'attitude_rating']:
            dimension_data = Evaluation.objects.filter(is_deleted=False).values(field).annotate(
                count=Count('id')
            ).order_by(field)
            result[field] = list(dimension_data)
        
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='bad_reviews')
    def bad_reviews(self, request):
        """
        差评列表接口
        
        返回评分低于等于3星的评价列表。
        """
        reviews = Evaluation.objects.filter(
            is_deleted=False,
            rating__lte=3
        ).order_by('-created_at')[:20]
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='hide')
    def hide(self, request, pk=None):
        """
        隐藏评价接口
        
        管理员隐藏不当评价。
        """
        instance = self.get_object()
        instance.is_hidden = True
        instance.hidden_reason = request.data.get('reason', '')
        instance.save()
        return Response({'code': 200, 'message': '已隐藏'})
    
    @action(detail=True, methods=['post'], url_path='show')
    def show(self, request, pk=None):
        """
        显示评价接口
        
        管理员取消隐藏评价。
        """
        instance = self.get_object()
        instance.is_hidden = False
        instance.hidden_reason = ''
        instance.save()
        return Response({'code': 200, 'message': '已显示'})

    @action(detail=True, methods=['post'], url_path='admin_review')
    def admin_review(self, request, pk=None):
        """
        管理员审核评价接口
        
        管理员审核评价内容，可以批准或拒绝。
        """
        evaluation = self.get_object()
        action_type = request.data.get('action')
        reply = request.data.get('reply', '')

        if action_type == 'approve':
            evaluation.is_reviewed = True
            evaluation.review_reply = reply or '审核通过'
        elif action_type == 'reject':
            evaluation.is_deleted = True
            evaluation.review_reply = reply or '审核不通过，已隐藏'
        else:
            return Response({'code': 400, 'message': '无效操作'}, status=status.HTTP_400_BAD_REQUEST)

        evaluation.reviewed_at = timezone.now()
        evaluation.save()

        return Response({'code': 200, 'message': f'已{"通过" if action_type == "approve" else "拒绝"}审核'})


class RepairRecordViewSet(viewsets.ModelViewSet):
    """
    维修记录视图集
    
    提供维修记录的查询和审核功能。
    主要用于管理员查看和审核维修记录。
    """
    
    serializer_class = RepairOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'staff']
    search_fields = ['repair_no', 'equipment_name', 'user_name']

    def get_queryset(self):
        """
        获取维修记录查询集
        
        不同身份的用户看到不同的维修记录：
        - 管理员：可以查看所有维修记录，支持按维修人员筛选
        - 维修人员：只能查看自己的维修记录
        - 默认返回已完成的工单
        """
        user_type, user_id, identity = get_request_identity(self.request)
        qs = RepairOrder.objects.filter(is_deleted=False).select_related('equipment', 'equipment_type', 'user', 'staff').prefetch_related('used_parts__spare_part')

        if getattr(self, 'action', None) == 'list':
            qs = qs.defer('remark', 'review_reply', 'description')

        if user_type == 'admin':
            staff_id_param = self.request.query_params.get('staff_id')
            if staff_id_param:
                qs = qs.filter(staff_id=staff_id_param)
        elif user_type == 'staff':
            qs = qs.filter(staff_id=user_id)
        elif user_type == 'user':
            qs = qs.filter(user_id=user_id)
        else:
            return RepairOrder.objects.none()
        
        # 处理工单编号筛选
        repair_no = self.request.query_params.get('repair_no')
        if repair_no:
            return qs.filter(repair_no=repair_no)
        
        # 处理状态筛选，默认返回已完成的工单
        status_param = self.request.query_params.get('status')
        if not status_param and not repair_no:
            qs = qs.filter(status='CLOSED')
        
        return qs

    def get_serializer_class(self):
        if getattr(self, 'action', None) == 'list':
            return RepairOrderListSerializer
        return RepairOrderSerializer

    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, pk=None):
        """
        审核维修记录接口
        
        管理员审核维修记录。
        """
        order = self.get_object()
        review_status = request.data.get('review_status')
        review_reply = request.data.get('review_reply', '')

        if review_status not in ('approved', 'rejected'):
            return Response({'code': 400, 'message': '无效的审核状态'}, status=400)

        if review_status == 'approved':
            order.status = 'CLOSED'
            if order.equipment_id and order.fault_count > 0:
                try:
                    eq = Equipment.objects.get(id=order.equipment_id)
                    eq.fault_count = max(0, eq.fault_count - order.fault_count)
                    eq.save()
                except Equipment.DoesNotExist:
                    pass
        else:
            order.status = 'IN_PROGRESS'

        order.review_reply = review_reply
        order.review_time = timezone.now()
        order.save()

        return Response({'code': 200, 'message': '审核成功'})


class EvaluationAppealViewSet(viewsets.ModelViewSet):
    
    queryset = EvaluationAppeal.objects.all()
    serializer_class = EvaluationAppealSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        qs = EvaluationAppeal.objects.all()
        user_type, user_id, identity = get_request_identity(self.request)
        if user_type == 'staff' and user_id:
            qs = qs.filter(staff_id=user_id)
        return qs

    def create(self, request, *args, **kwargs):
        evaluation_id = request.data.get('evaluation')
        if not evaluation_id:
            return Response({'code': 400, 'message': '请选择要申诉的评价'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
        except Evaluation.DoesNotExist:
            return Response({'code': 404, 'message': '评价不存在'}, status=status.HTTP_404_NOT_FOUND)

        three_days_ago = timezone.now() - timedelta(days=3)
        if evaluation.created_at < three_days_ago:
            return Response({'code': 400, 'message': '超过3天的评价不可申诉'}, status=status.HTTP_400_BAD_REQUEST)

        existing_appeal = EvaluationAppeal.objects.filter(evaluation=evaluation).first()
        if existing_appeal:
            if existing_appeal.status == 'pending':
                return Response({'code': 400, 'message': '该评价已有待处理的申诉'}, status=400)
            if existing_appeal.status == 'approved':
                return Response({'code': 400, 'message': '该评价申诉已通过，等待用户重新评价'}, status=400)
            if existing_appeal.status == 'rejected':
                return Response({'code': 400, 'message': '该评价申诉已被驳回，不可再次申诉'}, status=400)

        data = request.data.copy()
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'staff' and identity:
            data['staff'] = identity.id
            data['staff_name'] = identity.real_name
        data['status'] = 'pending'

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({'code': 200, 'message': '申诉提交成功，等待管理员审核', 'data': serializer.data}, status=201)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        appeal = self.get_object()
        if appeal.status != 'pending':
            return Response({'code': 400, 'message': '该申诉已处理'}, status=400)
        
        appeal.status = 'approved'
        user_type, user_id, identity = get_request_identity(request)
        appeal.handler = str(identity) if identity else ''
        appeal.handle_time = timezone.now()
        appeal.reply = request.data.get('reply', '申诉已通过')
        appeal.save()
        
        evaluation = appeal.evaluation
        evaluation.is_hidden = True
        evaluation.hidden_reason = '申诉通过，等待用户重新评价'
        evaluation.save()
        
        return Response({'code': 200, 'message': '申诉已通过，用户可重新评价'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        appeal = self.get_object()
        if appeal.status != 'pending':
            return Response({'code': 400, 'message': '该申诉已处理'}, status=400)
        
        appeal.status = 'rejected'
        user_type, user_id, identity = get_request_identity(request)
        appeal.handler = str(identity) if identity else ''
        appeal.handle_time = timezone.now()
        appeal.reply = request.data.get('reply', '申诉未通过')
        appeal.save()
        
        return Response({'code': 200, 'message': '申诉已驳回'})
