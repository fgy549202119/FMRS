"""
Django项目URL路由配置文件

该模块是设施管理与报修系统(FMRS)的总URL路由入口，负责：
- 注册各功能模块的API路由
- 配置管理后台入口
- 配置文件上传接口
- 在开发环境下提供静态文件和媒体文件的访问路由

路由结构：
- /admin/          -> Django管理后台
- /api/user/       -> 用户管理模块API
- /api/equipment/  -> 设备管理模块API
- /api/repair/     -> 报修管理模块API
- /api/announcement/ -> 公告管理模块API
- /api/inspection/ -> 巡检管理模块API
- /api/common/     -> 公共模块API
- /api/upload/     -> 文件上传接口

作者：FMRS开发者-范广宇
创建日期：2026年
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .upload_views import upload_image

# URL路由列表
# 定义项目的所有URL路径与视图函数的映射关系
urlpatterns = [
    # Django管理后台入口
    # 访问 /admin/ 可进入Django自带的管理界面
    path('admin/', admin.site.urls),
    
    # 用户管理模块API路由
    # 包含用户注册、登录、个人信息管理等功能
    path('api/user/', include('users.urls')),
    
    # 设备管理模块API路由
    # 包含设备信息管理、设备类型管理、位置管理等功能
    path('api/equipment/', include('equipment.urls')),
    
    # 报修管理模块API路由
    # 包含报修工单管理、维修记录、评价管理等功能
    path('api/repair/', include('repair.urls')),
    
    # 公告管理模块API路由
    # 包含系统公告的发布与管理功能
    path('api/announcement/', include('announcement.urls')),
    
    # 巡检管理模块API路由
    # 包含设备巡检任务的创建与执行功能
    path('api/inspection/', include('inspection.urls')),
    
    # 公共模块API路由
    # 包含备件管理、知识库管理等功能
    path('api/common/', include('common.urls')),
    
    path('api/location/', include('location.urls')),
    
    path('api/upload/', upload_image, name='upload'),
]

# 开发环境下的静态文件和媒体文件路由配置
# 仅在DEBUG模式下生效，生产环境由Nginx等Web服务器处理
if settings.DEBUG:
    # 媒体文件路由
    # 将 /media/ 路径映射到MEDIA_ROOT目录，用于访问用户上传的文件
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # 静态文件路由
    # 将 /static/ 路径映射到STATIC_ROOT目录，用于访问CSS、JS等静态资源
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
