"""
巡检管理模块 - 序列化器定义

该模块定义了巡检管理相关的序列化器，用于：
- 将模型实例转换为JSON格式的响应数据
- 将请求数据反序列化为模型实例

序列化器结构：
    InspectionRecordSerializer
        - 巡检记录的序列化
    
    InspectionSerializer
        - 巡检单的序列化
        - 包含关联的巡检记录列表
        - 包含设备类型名称、位置信息等计算字段

作者：范广宇
创建日期：2026年
"""

from rest_framework import serializers
from .models import Inspection, InspectionRecord


class InspectionRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = InspectionRecord
        fields = '__all__'


class InspectionListSerializer(serializers.ModelSerializer):
    equipment_name = serializers.ReadOnlyField(source='equipment.equipment_name', default='')
    equipment_type_name = serializers.ReadOnlyField(source='equipment.equipment_type.type_name', default='')
    has_photo = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Inspection
        fields = [
            'id', 'inspection_no', 'equipment', 'equipment_name', 'equipment_type_name',
            'equipment_sequence_number',
            'location', 'inspection_count', 'staff_name', 'inspection_time',
            'status', 'result', 'has_photo', 'created_at',
        ]


class InspectionSerializer(serializers.ModelSerializer):
    """
    巡检单序列化器
    
    用于巡检单的序列化和反序列化，包含关联的巡检记录列表。
    
    计算字段：
        - records: 关联的巡检记录列表
        - equipment_type_name: 设备类型名称
        - campus_name: 校区名称
        - building_name: 楼栋名称
        - floor_display: 楼层显示
    
    只读字段：
        - inspection_no: 巡检单号（自动生成）
        - staff_no: 巡检人员账号（自动填充）
        - staff_name: 巡检人员姓名（自动填充）
        - location: 设备位置（自动拼接）
    
    使用场景：
        - 巡检单列表查询
        - 巡检单详情查询
        - 巡检单创建和更新
    """
    
    # 关联的巡检记录列表
    records = InspectionRecordSerializer(many=True, read_only=True)
    
    # 设备名称
    equipment_name = serializers.ReadOnlyField(source='equipment.equipment_name', default='')
    # 设备类型名称
    equipment_type_name = serializers.ReadOnlyField(source='equipment.equipment_type.type_name', default='')
    
    # 校区名称
    campus_name = serializers.ReadOnlyField(source='campus.name', default='')
    
    # 楼栋名称
    building_name = serializers.ReadOnlyField(source='building.name', default='')
    
    # 楼层显示
    floor_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Inspection
        fields = '__all__'
        # 只读字段，不能通过API修改
        read_only_fields = ['inspection_no', 'staff_no', 'staff_name', 'location']
    
    def get_floor_display(self, obj):
        """
        获取楼层显示字符串
        
        参数：
            obj: Inspection实例
            
        返回值：
            str: 楼层显示字符串，如"3层"
        """
        if obj.floor:
            return f'{obj.floor.floor_number}层'
        return ''
