"""
公共模块 - 序列化器定义

该模块定义了公共功能相关的序列化器，用于：
- 将模型实例转换为JSON格式的响应数据
- 将请求数据反序列化为模型实例

序列化器结构：
    SparePartSerializer
        - 备件信息的序列化
        - 包含单位显示名称
    
    SparePartRecordSerializer
        - 备件记录的序列化
        - 包含备件名称和记录类型显示
    
    RepairLogSerializer
        - 维修日志的序列化
    
    RepairSparePartSerializer
        - 维修备件使用的序列化
        - 包含备件名称和编号
    
    KnowledgeBaseSerializer
        - 知识库的序列化
        - 包含分类显示名称

作者：范广宇
创建日期：2026年
"""

from rest_framework import serializers
from .models import SparePart, SparePartRecord, RepairLog, RepairSparePart, KnowledgeBase


class SparePartSerializer(serializers.ModelSerializer):
    """
    备件信息序列化器
    
    用于备件信息的序列化和反序列化。
    
    计算字段：
        - unit_display: 单位显示名称
    
    只读字段：
        - created_at: 创建时间
        - updated_time: 更新时间
    
    使用场景：
        - 备件列表查询
        - 备件详情查询
        - 备件创建和更新
    """
    
    # 单位显示名称
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = SparePart
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_time']


class SparePartRecordSerializer(serializers.ModelSerializer):
    """
    备件记录序列化器
    
    用于备件记录的序列化。
    
    计算字段：
        - part_name: 备件名称
        - record_type_display: 记录类型显示名称
    
    只读字段：
        - created_at: 创建时间
    
    使用场景：
        - 备件记录列表查询
        - 备件记录详情查询
    """
    
    # 备件名称
    part_name = serializers.CharField(source='part.name', read_only=True)
    
    # 记录类型显示名称
    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)

    class Meta:
        model = SparePartRecord
        fields = '__all__'
        read_only_fields = ['created_at']


class RepairLogSerializer(serializers.ModelSerializer):
    """
    维修日志序列化器
    
    用于维修日志的序列化和反序列化。
    
    只读字段：
        - created_at: 创建时间
    
    使用场景：
        - 维修日志列表查询
        - 维修日志创建
    """
    
    class Meta:
        model = RepairLog
        fields = '__all__'
        read_only_fields = ['created_at']


class RepairSparePartSerializer(serializers.ModelSerializer):
    """
    维修备件使用序列化器
    
    用于维修备件使用记录的序列化和反序列化。
    
    计算字段：
        - part_name: 备件名称
        - part_no: 备件编号
    
    只读字段：
        - total_price: 总价（自动计算）
        - created_at: 创建时间
    
    使用场景：
        - 维修备件使用列表查询
        - 维修备件使用记录创建
    """
    
    # 备件名称
    part_name = serializers.CharField(source='spare_part.name', read_only=True)
    
    # 备件编号
    part_no = serializers.CharField(source='spare_part.part_no', read_only=True)

    class Meta:
        model = RepairSparePart
        fields = '__all__'
        read_only_fields = ['total_price', 'created_at']


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """
    知识库序列化器
    
    用于知识库条目的序列化和反序列化。
    
    计算字段：
        - equipment_type_name: 设备类型名称
    
    只读字段：
        - view_count: 浏览次数
        - useful_count: 有用次数
        - created_at: 创建时间
        - updated_at: 更新时间
    
    使用场景：
        - 知识库列表查询
        - 知识库详情查询
        - 知识库创建和更新
    """
    
    # 设备类型名称
    equipment_type_name = serializers.CharField(source='equipment_type.type_name', read_only=True)
    keywords = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = KnowledgeBase
        fields = '__all__'
        read_only_fields = ['view_count', 'useful_count', 'created_at', 'updated_at']

    def validate_keywords(self, value):
        if value is None:
            return ''
        return value
