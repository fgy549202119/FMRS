"""
公告管理模块 - 视图函数定义

该模块提供了公告管理相关的API视图。

视图集结构：
    AnnouncementViewSet
        - 公告CRUD操作
        - 支持按标题和内容搜索

作者：范广宇
创建日期：2026年
"""

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    公告视图集
    
    提供公告的完整CRUD操作。
    
    继承自ModelViewSet，自动提供：
        - list: 获取公告列表
        - create: 创建公告
        - retrieve: 获取公告详情
        - update: 更新公告
        - destroy: 删除公告
    
    过滤功能：
        - 按标题搜索
        - 按内容搜索
    
    排序：
        - 默认按发布时间倒序排列
    """
    
    # 查询集
    queryset = Announcement.objects.all()
    
    # 序列化器
    serializer_class = AnnouncementSerializer
    
    # 过滤后端
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # 可搜索字段
    search_fields = ['title', 'content']
