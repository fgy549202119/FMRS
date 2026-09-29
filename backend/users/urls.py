"""
用户管理模块 - URL路由配置

用户管理相关的URL路由，使用DRF的路由器自动生成RESTful API。

路由结构：
    /api/user/users/              -> UserViewSet (用户管理)
        - GET    /                -> 获取用户列表
        - POST   /                -> 创建用户（注册）
        - GET    /{id}/           -> 获取单个用户详情
        - PUT    /{id}/           -> 更新用户信息
        - PATCH  /{id}/           -> 部分更新用户信息
        - DELETE /{id}/           -> 删除用户
        - POST   /login/          -> 用户登录
        - POST   /logout/         -> 用户登出
        - GET    /profile/        -> 获取当前用户信息
        - POST   /change_password/ -> 修改密码
        - POST   /batch_delete/   -> 批量删除用户
    
    /api/user/staff/              -> RepairStaffViewSet (维修人员管理)
        - GET    /                -> 获取维修人员列表
        - POST   /                -> 创建维修人员
        - GET    /{id}/           -> 获取单个维修人员详情
        - PUT    /{id}/           -> 更新维修人员信息
        - PATCH  /{id}/           -> 部分更新
        - DELETE /{id}/           -> 删除维修人员
        - POST   /login/          -> 维修人员登录
    
    /api/user/admin/             -> AdministratorViewSet (管理员管理)
        - GET    /                -> 获取管理员列表
        - POST   /                -> 创建管理员
        - GET    /{id}/           -> 获取单个管理员详情
        - PUT    /{id}/           -> 更新管理员信息
        - PATCH  /{id}/           -> 部分更新管理员信息
        - DELETE /{id}/           -> 删除管理员
        - POST   /login/          -> 管理员登录

作者：范广宇
创建日期：2026年
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RepairStaffViewSet, AdministratorViewSet, MessageBoardViewSet

# 创建DRF默认路由器
# DefaultRouter会自动生成标准的RESTful路由
router = DefaultRouter()

# 注册用户视图集
# 路由前缀：users，对应UserViewSet
router.register(r'users', UserViewSet)

# 注册维修人员视图集
# 路由前缀：staff，对应RepairStaffViewSet
router.register(r'staff', RepairStaffViewSet)

# 注册管理员视图集
# 路由前缀：admin，对应AdministratorViewSet
router.register(r'admin', AdministratorViewSet)

router.register(r'messages', MessageBoardViewSet)

# URL配置
# 将路由器的URL包含在urlpatterns中
urlpatterns = [
    path('', include(router.urls)),
]
