"""
设备管理模块 - 视图函数定义

该模块提供了设备管理相关的API视图，包括：
- 校区管理（CampusViewSet）
- 楼栋管理（BuildingViewSet）
- 楼层管理（FloorViewSet）
- 设备类型管理（EquipmentTypeViewSet）
- 设备类型申请管理（EquipmentTypeRequestViewSet）
- 设备管理（EquipmentViewSet）

视图集结构：
    CampusViewSet
        - 校区CRUD操作
        - 获取校区选项列表
    
    BuildingViewSet
        - 楼栋CRUD操作
        - 按校区过滤
    
    FloorViewSet
        - 楼层CRUD操作
        - 批量创建楼层
        - 按楼栋查询
    
    EquipmentTypeViewSet
        - 设备类型CRUD操作
        - 统计功能
        - 删除前检查关联设备
    
    EquipmentTypeRequestViewSet
        - 申请CRUD操作
        - 审核功能
    
    EquipmentViewSet
        - 设备CRUD操作
        - 统计功能

作者：FMRS开发者范广宇
创建日期：2026年
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .models import EquipmentType, Equipment, EquipmentTypeRequest
from .serializers import (EquipmentTypeSerializer, EquipmentTypeSimpleSerializer,
                          EquipmentSerializer, EquipmentTypeRequestSerializer)
from .filters import EquipmentFilter
from backend.authentication import get_request_identity


class AdminWritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve', 'options', 'statistics', 'batch_delete', 'distinct_names', 'by_name_and_location']:
            return True
        user_type, _, _ = get_request_identity(request)
        return user_type == 'admin'


class EquipmentTypeViewSet(viewsets.ModelViewSet):
    """
    设备类型视图集
    
    提供设备类型的完整CRUD操作，包含统计功能。
    
    继承自ModelViewSet，自动提供CRUD操作。
    
    过滤功能：
        - 按类型名称搜索
        - 按类型编码搜索
        - 按排序字段排序
        - 按创建时间排序
    
    自定义操作：
        - statistics: 设备类型统计
        - options: 获取启用的设备类型选项
    
    删除限制：
        - 有关联设备的类型不能删除
    """
    
    # 查询集
    queryset = EquipmentType.objects.all()
    
    # 序列化器
    serializer_class = EquipmentTypeSerializer
    
    permission_classes = [AdminWritePermission]
    
    # 过滤后端
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    
    # 可搜索字段
    search_fields = ['type_name', 'type_code']
    
    # 可排序字段
    ordering_fields = ['sort_order', 'created_at']
    
    # 默认排序
    ordering = ['sort_order', '-created_at']

    def create(self, request, *args, **kwargs):
        """
        创建设备类型
        
        请求方式：
            POST /api/equipment/types/
        
        返回格式：
            {'code': 200, 'message': '创建成功', 'data': {类型信息}}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'code': 200,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        更新设备类型
        
        请求方式：
            PUT/PATCH /api/equipment/types/{id}/
        
        返回格式：
            {'code': 200, 'message': '更新成功', 'data': {类型信息}}
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_name = instance.type_name
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 如果类型名称变更，更新关联设备
        new_name = serializer.data.get('type_name')
        if old_name != new_name:
            Equipment.objects.filter(equipment_type=instance).update(
                equipment_type=instance
            )

        return Response({
            'code': 200,
            'message': '更新成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        删除设备类型
        
        删除前检查是否有关联设备，有则不允许删除。
        
        请求方式：
            DELETE /api/equipment/types/{id}/
        
        返回格式：
            成功：{'code': 200, 'message': '删除成功'}
            失败：{'code': 400, 'message': '该设备类型下有 N 个设备，无法删除'}
        """
        instance = self.get_object()
        
        # 检查是否有关联设备
        equipment_count = Equipment.objects.filter(equipment_type=instance).count()
        if equipment_count > 0:
            return Response({
                'code': 400,
                'message': f'该设备类型下有 {equipment_count} 个设备，无法删除'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        from django.core.cache import cache

        cache_key = 'equip_type_stats'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        total_types = EquipmentType.objects.count()
        total_equipment = Equipment.objects.count()
        total_fault = Equipment.objects.aggregate(total=Sum('fault_count'))['total'] or 0

        type_stats = EquipmentType.objects.annotate(
            equipment_count=Count('equipment'),
            fault_count_sum=Sum('equipment__fault_count')
        ).values('id', 'type_name', 'equipment_count', 'fault_count_sum')

        # 按校区统计：单条SQL聚合，替代遍历3万+设备
        from location.models import Campus
        valid_campus_names = list(Campus.objects.values_list('name', flat=True).order_by('sort_order', 'id'))
        campus_agg = (
            Equipment.objects
            .filter(building__isnull=False)
            .values('building__campus__name')
            .annotate(cnt=Count('id'))
        )
        campus_distribution = {item['building__campus__name']: item['cnt'] for item in campus_agg}
        ordered_campus = {name: campus_distribution.get(name, 0) for name in valid_campus_names}

        result = {
            'total_types': total_types,
            'total_equipment': total_equipment,
            'total_fault': total_fault,
            'type_stats': list(type_stats),
            'campus_distribution': ordered_campus,
        }
        cache.set(cache_key, result, 60)
        return Response(result)

    @action(detail=False, methods=['get'])
    def options(self, request):
        """
        获取启用的设备类型选项
        
        返回启用状态的设备类型列表，用于下拉选择。
        
        请求方式：
            GET /api/equipment/types/options/
        
        返回格式：
            [{id, type_name, type_code, icon}, ...]
        """
        types = EquipmentType.objects.all().values('id', 'type_name', 'type_code', 'icon')
        return Response(list(types))


class EquipmentTypeRequestViewSet(viewsets.ModelViewSet):
    """
    设备类型申请视图集
    
    提供设备类型申请的完整管理功能。
    
    继承自ModelViewSet，自动提供CRUD操作。
    
    自定义操作：
        - review_request: 审核申请
    
    创建逻辑：
        - 自动关联当前用户为申请人
    """
    
    # 查询集
    queryset = EquipmentTypeRequest.objects.all()
    
    # 序列化器
    serializer_class = EquipmentTypeRequestSerializer

    def perform_create(self, serializer):
        """
        创建申请时自动关联申请人
        
        参数：
            serializer: 序列化器实例
        """
        if self.request.user.is_authenticated:
            serializer.save(applicant=self.request.user)

    @action(detail=True, methods=['post'], url_path='review')
    def review_request(self, request, pk=None):
        """
        审核申请
        
        管理员审核设备类型申请。
        审核通过后自动创建设备类型。
        
        请求方式：
            POST /api/equipment/type-requests/{id}/review/
        
        请求参数：
            - status: 审核状态（approved/rejected）
            - reply: 审核回复
        
        返回格式：
            成功：{'code': 200, 'message': '审核通过，设备类型已创建'}
        """
        instance = self.get_object()
        review_status = request.data.get('status')
        review_reply = request.data.get('reply', '')

        # 更新申请状态
        instance.status = review_status
        instance.reviewer = request.user
        instance.review_reply = review_reply
        instance.review_time = timezone.now()
        instance.save()

        # 审核通过后创建设备类型
        if review_status == 'approved':
            equipment_type, created = EquipmentType.objects.update_or_create(
                type_name=instance.type_name,
                defaults={
                    'description': instance.description,
                }
            )
            return Response({'code': 200, 'message': '审核通过，设备类型已创建'})

        return Response({'code': 200, 'message': f'审核结果已反馈'})


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    设备视图集
    
    提供设备的完整CRUD操作，包含统计功能。
    
    继承自ModelViewSet，自动提供CRUD操作。
    
    过滤功能：
        - 按设备类型过滤
        - 按设备状态过滤
        - 按设备名称搜索
        - 按设备编号搜索
    
    自定义操作：
        - statistics: 设备统计
    """
    
    # 查询集：预加载设备类型信息和位置信息
    queryset = Equipment.objects.select_related('equipment_type', 'room', 'room__floor', 'room__floor__building', 'room__floor__building__campus', 'floor', 'floor__building', 'floor__building__campus', 'building', 'building__campus').all()
    
    # 序列化器
    serializer_class = EquipmentSerializer
    
    permission_classes = [AdminWritePermission]
    
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    
    filterset_class = EquipmentFilter
    
    search_fields = ['equipment_name', 'equipment_no', 'sequence_number']

    def create(self, request, *args, **kwargs):
        """
        创建设备
        
        请求方式：
            POST /api/equipment/list/
        
        返回格式：
            {'code': 200, 'message': '创建成功', 'data': {设备信息}}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'code': 200,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        更新设备
        
        请求方式：
            PUT/PATCH /api/equipment/list/{id}/
        
        返回格式：
            {'code': 200, 'message': '更新成功', 'data': {设备信息}}
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """
        删除设备
        
        请求方式：
            DELETE /api/equipment/list/{id}/
        
        返回格式：
            {'code': 200, 'message': '删除成功'}
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        设备统计

        返回设备相关的统计数据。

        请求方式：
            GET /api/equipment/list/statistics/

        返回格式：
            {
                'total': 设备总数,
                'normal_count': 正常设备数,
                'fault_count': 故障设备数,
                'total_fault': 故障总数
            }
        """
        from django.core.cache import cache

        cache_key = 'equip_stats'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # 统计总数
        total = Equipment.objects.count()

        # 统计正常设备（无故障）
        normal_count = Equipment.objects.filter(fault_count=0).count()

        # 统计故障设备（有故障）
        fault_count = Equipment.objects.filter(fault_count__gt=0).count()

        # 统计故障总数
        total_fault = Equipment.objects.aggregate(total=Sum('fault_count'))['total'] or 0

        result = {
            'total': total,
            'normal_count': normal_count,
            'fault_count': fault_count,
            'total_fault': total_fault
        }
        cache.set(cache_key, result, 60)
        return Response(result)

    @action(detail=False, methods=['post'], url_path='batch_delete')
    def batch_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'code': 400, 'message': '请提供要删除的设备ID列表'}, status=status.HTTP_400_BAD_REQUEST)

        existing = Equipment.objects.filter(id__in=ids)
        deleted_count = existing.count()
        existing.delete()

        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 台设备',
            'deleted_count': deleted_count,
        })

    @action(detail=False, methods=['get'], url_path='distinct_names')
    def distinct_names(self, request):
        search = request.query_params.get('search', '')

        distinct_eqs = Equipment.objects.values('equipment_name').annotate(
            count=Count('id')
        ).order_by('equipment_name')

        if search:
            distinct_eqs = distinct_eqs.filter(equipment_name__icontains=search)

        results = []
        for item in distinct_eqs:
            rep = Equipment.objects.filter(
                equipment_name=item['equipment_name']
            ).select_related('equipment_type').first()

            if rep:
                results.append({
                    'id': rep.id,
                    'equipment_name': rep.equipment_name,
                    'equipment_type': rep.equipment_type_id,
                    'equipment_type_name': rep.equipment_type.type_name if rep.equipment_type else '',
                    'equipment_type_detail': {
                        'id': rep.equipment_type_id,
                        'type_name': rep.equipment_type.type_name if rep.equipment_type else '',
                        'type_code': rep.equipment_type.type_code if rep.equipment_type else '',
                        'icon': rep.equipment_type.icon if rep.equipment_type else '',
                    } if rep.equipment_type else None,
                    'equipment_image': rep.equipment_image or '',
                    'specification': rep.specification or '',
                    'status': rep.status,
                    'is_reportable': rep.is_reportable,
                    'count': item['count'],
                })

        return Response({'results': results, 'count': len(results)})

    @action(detail=False, methods=['get'], url_path='by_name_and_location')
    def by_name_and_location(self, request):
        equipment_name = request.query_params.get('equipment_name', '')
        room_id = request.query_params.get('room_id')
        floor_id = request.query_params.get('floor_id')
        building_id = request.query_params.get('building_id')

        if not equipment_name:
            return Response({'results': [], 'count': 0})

        queryset = Equipment.objects.filter(equipment_name=equipment_name)

        if room_id:
            queryset = queryset.filter(room_id=room_id)
        elif floor_id:
            queryset = queryset.filter(floor_id=floor_id)
        elif building_id:
            queryset = queryset.filter(building_id=building_id)

        queryset = queryset.order_by('sequence_number')

        results = []
        for eq in queryset:
            results.append({
                'id': eq.id,
                'sequence_number': eq.sequence_number,
                'equipment_name': eq.equipment_name,
                'status': eq.status,
            })

        return Response({'results': results, 'count': len(results)})
