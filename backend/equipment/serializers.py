"""
设备管理模块 - 序列化器定义

该模块定义了设备管理相关的序列化器，用于：
- 将模型实例转换为JSON格式的响应数据
- 将请求数据反序列化为模型实例
- 数据验证和关联数据处理

序列化器结构：
    CampusSerializer
        - 校区信息的序列化
        - 包含楼栋数量统计
    
    BuildingSerializer
        - 楼栋信息的序列化
        - 包含校区名称
    
    FloorSerializer
        - 楼层信息的序列化
        - 包含楼栋和校区信息
    
    EquipmentTypeSerializer
        - 设备类型的完整序列化
        - 包含设备数量和故障统计
    
    EquipmentTypeSimpleSerializer
        - 设备类型的简化序列化
        - 用于下拉选择等场景
    
    EquipmentTypeRequestSerializer
        - 设备类型申请的序列化
    
    EquipmentSerializer
        - 设备信息的序列化
        - 包含设备类型详情

作者：范广宇
创建日期：2026年
"""

from rest_framework import serializers
from .models import EquipmentType, Equipment, EquipmentTypeRequest
from django.db.models import Count, Sum


class EquipmentTypeSerializer(serializers.ModelSerializer):
    """
    设备类型序列化器
    
    用于设备类型的完整序列化，包含统计信息。
    
    计算字段：
        - equipment_count: 该类型的设备数量
        - fault_equipment_count: 该类型的故障设备数量
        - total_fault_count: 该类型的故障总数
    
    使用场景：
        - 设备类型列表查询
        - 设备类型详情查询
        - 设备类型创建和更新
    """
    
    # 设备数量
    equipment_count = serializers.SerializerMethodField()
    
    # 故障设备数量
    fault_equipment_count = serializers.SerializerMethodField()
    
    # 故障总数
    total_fault_count = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentType
        fields = '__all__'

    def get_equipment_count(self, obj):
        """
        获取该类型的设备数量
        
        参数：
            obj: EquipmentType实例
            
        返回值：
            int: 设备数量
        """
        return Equipment.objects.filter(equipment_type=obj).count()

    def get_fault_equipment_count(self, obj):
        """
        获取该类型的故障设备数量
        
        参数：
            obj: EquipmentType实例
            
        返回值：
            int: 故障设备数量
        """
        return Equipment.objects.filter(equipment_type=obj, fault_count__gt=0).count()

    def get_total_fault_count(self, obj):
        """
        获取该类型的故障总数
        
        参数：
            obj: EquipmentType实例
            
        返回值：
            int: 故障总数
        """
        result = Equipment.objects.filter(equipment_type=obj).aggregate(total=Sum('fault_count'))
        return result['total'] or 0


class EquipmentTypeSimpleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EquipmentType
        fields = ['id', 'type_name', 'type_code', 'icon']


class EquipmentTypeRequestSerializer(serializers.ModelSerializer):
    """
    设备类型申请序列化器
    
    用于设备类型申请的序列化和反序列化。
    
    只读字段：
        - applicant_name: 申请人姓名
        - status: 审核状态
        - reviewer: 审核人
        - review_reply: 审核回复
    
    使用场景：
        - 申请列表查询
        - 申请详情查询
        - 申请创建
    """
    
    # 申请人姓名
    applicant_name = serializers.CharField(read_only=True)

    class Meta:
        model = EquipmentTypeRequest
        fields = '__all__'
        # 只读字段，不能通过API修改
        read_only_fields = ['applicant', 'applicant_name', 'status', 'reviewer', 'review_reply']


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type_name = serializers.CharField(source='equipment_type.type_name', default='', read_only=True)
    equipment_type_code = serializers.CharField(source='equipment_type.type_code', default='', read_only=True)
    equipment_type_icon = serializers.CharField(source='equipment_type.icon', default='', read_only=True)
    equipment_type_detail = serializers.SerializerMethodField()
    location_info = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = ['id', 'sequence_number', 'equipment_no', 'equipment_name', 'equipment_type', 'equipment_type_name',
                  'equipment_type_code', 'equipment_type_icon', 'equipment_type_detail',
                  'equipment_image', 'specification', 'fault_count', 'status',
                  'is_reportable', 'supplier', 'building', 'floor', 'room', 'location_info',
                  'publish_time', 'created_at', 'updated_at']
        read_only_fields = ['equipment_no', 'sequence_number', 'fault_count', 'status', 'publish_time', 'created_at', 'updated_at']

    def get_equipment_type_detail(self, obj):
        if obj.equipment_type:
            return {
                'id': obj.equipment_type.id,
                'type_name': obj.equipment_type.type_name,
                'type_code': obj.equipment_type.type_code,
                'icon': obj.equipment_type.icon,
            }
        return None

    def get_location_info(self, obj):
        room_id = None
        room_name = '-'
        floor_id = None
        floor_number = '-'
        building_id = None
        building_name = '-'
        campus_id = None
        campus_name = '-'
        full_location = '-'
        
        if obj.room:
            room = obj.room
            room_id = room.id
            room_name = room.name
            if room.floor:
                floor = room.floor
                floor_id = floor.id
                floor_number = floor.floor_number
                if floor.building:
                    building = floor.building
                    building_id = building.id
                    building_name = building.name
                    if building.campus:
                        campus = building.campus
                        campus_id = campus.id
                        campus_name = campus.name
        elif obj.floor:
            floor = obj.floor
            floor_id = floor.id
            floor_number = floor.floor_number
            if floor.building:
                building = floor.building
                building_id = building.id
                building_name = building.name
                if building.campus:
                    campus = building.campus
                    campus_id = campus.id
                    campus_name = campus.name
        elif obj.building:
            building = obj.building
            building_id = building.id
            building_name = building.name
            if building.campus:
                campus = building.campus
                campus_id = campus.id
                campus_name = campus.name
        
        location_parts = []
        if campus_name != '-':
            location_parts.append(campus_name)
        if building_name != '-':
            location_parts.append(building_name)
        if floor_number != '-':
            location_parts.append(f'{floor_number}层')
        if room_name != '-':
            location_parts.append(room_name)
        
        full_location = ' '.join(location_parts) if location_parts else '-'
        
        return {
            'room_id': room_id,
            'room_name': room_name,
            'floor_id': floor_id,
            'floor_number': floor_number,
            'building_id': building_id,
            'building_name': building_name,
            'campus_id': campus_id,
            'campus_name': campus_name,
            'full_location': full_location,
        }
