"""
公告管理模块 - 序列化器定义

该模块定义了公告管理相关的序列化器，用于：
- 将模型实例转换为JSON格式的响应数据
- 将请求数据反序列化为模型实例

序列化器结构：
    AnnouncementSerializer
        - 公告信息的序列化和反序列化

作者：范广宇
创建日期：2026年
"""

from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    公告序列化器
    
    用于公告信息的序列化和反序列化。
    
    使用场景：
        - 公告列表查询
        - 公告详情查询
        - 公告创建和更新
    """
    
    class Meta:
        model = Announcement
        fields = '__all__'
