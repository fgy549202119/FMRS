"""
报修管理模块 - URL路由配置

该模块定义了报修管理相关的URL路由，使用DRF的路由器自动生成RESTful API。

路由结构：
    /api/repair/orders/              -> RepairOrderViewSet (报修工单管理)
        - GET    /                   -> 获取工单列表
        - POST   /                   -> 创建工单
        - GET    /{id}/              -> 获取单个工单详情
        - PUT    /{id}/              -> 更新工单信息
        - PATCH  /{id}/              -> 部分更新
        - DELETE /{id}/              -> 删除工单
        - POST   /check_duplicate/   -> 检查重复报修
        - POST   /{id}/accept/       -> 接单
        - POST   /{id}/complete/     -> 提交完成
        - POST   /{id}/review/       -> 审核
        - POST   /{id}/transfer/     -> 转派
        - DELETE /{id}/soft-delete/  -> 软删除
        - POST   /{id}/cancel/       -> 取消工单
        - GET    /online-staff-list/ -> 获取在线维修人员
        - GET    /statistics/        -> 工单统计
        - GET    /staff-ranking/     -> 维修人员排名
        - GET    /my-orders/         -> 我的工单
        - GET    /pending_evaluation/ -> 待评价工单
    
    /api/repair/evaluations/         -> EvaluationViewSet (评价管理)
        - GET    /                   -> 获取评价列表
        - POST   /                   -> 创建评价
        - GET    /{id}/              -> 获取单个评价详情
        - DELETE /{id}/              -> 删除评价
        - GET    /statistics/        -> 评价统计
        - GET    /check_evaluated/   -> 检查已评价工单
        - GET    /staff_ranking/     -> 维修人员评分排名
        - GET    /monthly_trend/     -> 月度趋势
        - GET    /dimension_analysis/ -> 维度分析
        - GET    /bad_reviews/       -> 差评列表
        - POST   /{id}/hide/         -> 隐藏评价
        - POST   /{id}/show/         -> 显示评价
        - POST   /{id}/admin_review/ -> 管理员审核
    
    /api/repair/appeals/             -> EvaluationAppealViewSet (评价申诉)
        - GET    /                   -> 获取申诉列表
        - POST   /                   -> 创建申诉
        - GET    /{id}/              -> 获取申诉详情
        - POST   /{id}/approve/      -> 通过申诉
        - POST   /{id}/reject/       -> 驳回申诉
    
    /api/repair/transfers/           -> TransferRecordViewSet (转派记录)
        - GET    /                   -> 获取转派记录列表
        - GET    /{id}/              -> 获取转派记录详情
    
    /api/repair/staff-online/        -> StaffOnlineStatusViewSet (在线状态)
        - GET    /                   -> 获取在线状态列表
        - POST   /heartbeat/         -> 心跳
        - POST   /logout/            -> 登出
        - POST   /set_status/        -> 设置状态
    
    /api/repair/attachments/         -> AttachmentViewSet (附件管理)
        - CRUD操作
    
    /api/repair/records/             -> RepairRecordViewSet (维修记录)
        - GET    /                   -> 获取维修记录列表
        - POST   /{id}/review/       -> 审核

作者：范广宇
创建日期：2026年
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RepairOrderViewSet, EvaluationViewSet, EvaluationAppealViewSet,
                    TransferRecordViewSet, StaffOnlineStatusViewSet, AttachmentViewSet,
                    RepairRecordViewSet)

# 创建DRF默认路由器
router = DefaultRouter()

# 注册报修工单视图集
router.register('orders', RepairOrderViewSet, basename='order')

# 注册评价视图集
router.register('evaluations', EvaluationViewSet, basename='evaluation')

# 注册评价申诉视图集
router.register('appeals', EvaluationAppealViewSet, basename='appeal')

# 注册转派记录视图集
router.register('transfers', TransferRecordViewSet, basename='transfer')

# 注册在线状态视图集
router.register('staff-online', StaffOnlineStatusViewSet, basename='staff-online')

# 注册附件视图集
router.register('attachments', AttachmentViewSet, basename='attachment')

# 注册维修记录视图集
router.register('records', RepairRecordViewSet, basename='record')

# URL配置
urlpatterns = [
    path('', include(router.urls)),
]
