"""
公共模块 - URL路由配置

该模块定义了公共功能相关的URL路由，使用DRF的路由器自动生成RESTful API。

路由结构：
    /api/common/spare-parts/         -> SparePartViewSet (备件管理)
        - CRUD操作
        - GET  /low_stock/            -> 库存不足列表
        - POST /{id}/stock_in/        -> 入库
        - POST /{id}/stock_out/       -> 出库
    
    /api/common/spare-part-records/  -> SparePartRecordViewSet (备件记录)
        - 只读查询
    
    /api/common/repair-logs/         -> RepairLogViewSet (维修日志)
        - CRUD操作
    
    /api/common/repair-spare-parts/  -> RepairSparePartViewSet (维修备件使用)
        - CRUD操作
    
    /api/common/knowledge/           -> KnowledgeBaseViewSet (知识库)
        - CRUD操作
        - POST /{id}/view/            -> 增加浏览次数
        - POST /{id}/useful/          -> 增加有用次数
    
    /api/common/export/              -> ExportViewSet (数据导出)
        - GET /repair_orders_excel/   -> 导出工单Excel
        - GET /repair_orders_pdf/     -> 导出工单PDF
        - GET /spare_parts_excel/     -> 导出备件Excel
    
    /api/common/stats/               -> StatsViewSet (统计数据)
        - GET /summary/               -> 系统概览统计

作者：范广宇
创建日期：2026年
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SparePartViewSet, SparePartRecordViewSet,
    RepairLogViewSet, RepairSparePartViewSet, KnowledgeBaseViewSet, ExportViewSet,
    StatsViewSet
)

# 创建DRF默认路由器
router = DefaultRouter()

# 注册备件视图集
router.register(r'spare-parts', SparePartViewSet)

# 注册备件记录视图集
router.register(r'spare-part-records', SparePartRecordViewSet)

# 注册维修日志视图集
router.register(r'repair-logs', RepairLogViewSet)

# 注册维修备件使用视图集
router.register(r'repair-spare-parts', RepairSparePartViewSet)

# 注册知识库视图集
router.register(r'knowledge', KnowledgeBaseViewSet)

# 注册数据导出视图集
router.register(r'export', ExportViewSet, basename='export')

# 注册统计数据视图集
router.register(r'stats', StatsViewSet, basename='stats')

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]
