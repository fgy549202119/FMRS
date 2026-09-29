"""
公告管理模块 - URL路由配置

该模块定义了公告管理相关的URL路由，使用DRF的路由器自动生成RESTful API。

路由结构：
    /api/announcement/list/         -> AnnouncementViewSet (公告管理)
        - GET    /                  -> 获取公告列表
        - POST   /                  -> 创建公告
        - GET    /{id}/             -> 获取公告详情
        - PUT    /{id}/             -> 更新公告
        - DELETE /{id}/             -> 删除公告

作者：范广宇
创建日期：2026年
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementViewSet

# 创建DRF默认路由器
router = DefaultRouter()

# 注册公告视图集
router.register(r'list', AnnouncementViewSet)

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]
