"""
巡检管理模块 - URL路由配置

该模块定义了巡检管理相关的URL路由，使用DRF的路由器自动生成RESTful API。

路由结构：
    /api/inspection/list/         -> InspectionViewSet (巡检单管理)
        - GET    /                -> 获取巡检单列表
        - POST   /                -> 创建巡检单
        - GET    /{id}/           -> 获取巡检单详情
        - PUT    /{id}/           -> 更新巡检单
        - DELETE /{id}/           -> 删除巡检单
        - POST   /{id}/review/    -> 审核巡检单
    
    /api/inspection/records/      -> InspectionRecordViewSet (巡检记录)
        - CRUD操作

作者：范广宇
创建日期：2026年
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InspectionViewSet, InspectionRecordViewSet

# 创建DRF默认路由器
router = DefaultRouter()

# 注册巡检单视图集
router.register(r'list', InspectionViewSet)

# 注册巡检记录视图集
router.register(r'records', InspectionRecordViewSet)

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]
