"""
Django项目核心配置文件

该模块是设施管理与报修系统(FMRS)的核心配置文件，包含以下关键配置：
- 数据库连接配置：MySQL数据库连接参数
- 已安装应用配置：系统各功能模块的注册
- 中间件配置：请求/响应处理管道
- REST Framework配置：API框架的全局设置
- 跨域配置：前后端分离架构的CORS设置
- 静态文件与媒体文件配置：文件存储路径设置

作者：FMRS开发者-范广宇
创建日期：2026年
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value or not value.strip():
        raise ImproperlyConfigured(f"{name} environment variable must be set")
    return value

# 项目根目录路径
# 通过当前文件路径向上解析两级目录，定位到backend目录
BASE_DIR = Path(__file__).resolve().parent.parent

# Django密钥
SECRET_KEY = _required_env('DJANGO_SECRET_KEY')

# 调试模式默认关闭，开发环境可显式开启
DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'

# 主机名默认仅允许本机，部署环境应提供实际域名
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        'DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1'
    ).split(',')
    if host.strip()
]

# 已安装应用配置
# 包含Django内置应用、第三方应用和项目自定义应用
INSTALLED_APPS = [
    # Django内置应用
    'django.contrib.admin',          # Django管理后台
    'django.contrib.auth',           # 用户认证系统
    'django.contrib.contenttypes',   # 内容类型框架
    'django.contrib.sessions',       # 会话框架
    'django.contrib.messages',       # 消息框架
    'django.contrib.staticfiles',    # 静态文件管理

    # 第三方应用
    'rest_framework',                # Django REST Framework，用于构建RESTful API
    'corsheaders',                   # Django CORS Headers，处理跨域请求
    'django_filters',                # Django Filters，提供查询过滤功能

    # 项目自定义应用
    'users',                         # 用户管理模块
    'equipment',                     # 设备管理模块
    'repair',                        # 报修管理模块
    'announcement',                  # 公告管理模块
    'inspection',                    # 巡检管理模块
    'common',                        # 公共模块（备件、知识库等）
    'location',                      # 位置管理模块
]

# 中间件配置
# 定义请求/响应的处理管道，按顺序执行
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',           # CORS中间件，必须放在最前面
    'django.middleware.security.SecurityMiddleware',   # 安全中间件
    'django.contrib.sessions.middleware.SessionMiddleware',  # 会话中间件
    'django.middleware.common.CommonMiddleware',       # 通用中间件
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',     # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # 点击劫持防护
]

# 根URL配置模块
ROOT_URLCONF = 'backend.urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # 模板引擎
        'DIRS': [],                    # 模板目录，空列表表示使用默认目录
        'APP_DIRS': True,              # 是否在应用目录中查找模板
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',      # 调试信息
                'django.template.context_processors.request',    # 请求对象
                'django.contrib.auth.context_processors.auth',   # 认证用户
                'django.contrib.messages.context_processors.messages',  # 消息
            ],
        },
    },
]

# WSGI应用入口
WSGI_APPLICATION = 'backend.wsgi.application'

# 数据库配置
# 使用MySQL数据库存储系统数据
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': _required_env('DB_NAME'),
        'USER': _required_env('DB_USER'),
        'PASSWORD': _required_env('DB_PASSWORD'),
        'HOST': _required_env('DB_HOST'),
        'PORT': _required_env('DB_PORT'),
        'CONN_MAX_AGE': 600,                    # 数据库连接持久化600秒
        'OPTIONS': {
            'charset': 'utf8mb4',               # 字符集，支持中文和emoji
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",  # SQL模式
        },
    }
}

# 密码验证器配置
# 空列表表示不使用密码复杂度验证，实际生产环境应配置验证器
AUTH_PASSWORD_VALIDATORS = []

# 国际化配置
LANGUAGE_CODE = 'zh-hans'           # 语言代码：简体中文
TIME_ZONE = 'Asia/Shanghai'         # 时区：上海时区（东八区）
USE_I18N = True                     # 启用国际化
USE_TZ = False                       # 禁用时区支持（修复MySQL日期查询问题）

# 静态文件配置
# 静态文件（CSS、JS、图片等）的URL前缀和存储路径
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# 媒体文件配置
# 用户上传文件的URL前缀和存储路径
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
# 使用users应用中的User模型替代Django默认的User模型
AUTH_USER_MODEL = 'users.User'

# 跨域资源共享(CORS)配置
# 允许所有来源的跨域请求，适用于开发环境
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True       # 允许携带认证信息（如Cookie）

# CSRF受信任来源
# 配置前端开发服务器的地址，允许跨站请求
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://127.0.0.1:3001']

# Django REST Framework配置
REST_FRAMEWORK = {
    # 认证类配置
    # 使用基于 Token 的独立鉴权，解决三端 Session 覆盖问题
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'backend.authentication.TokenAuthentication',
    ],
    # 权限类配置
    # AllowAny表示允许所有用户访问，具体权限在视图中单独控制
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # 过滤后端配置
    # 支持通过URL参数进行数据过滤
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    # 分页配置
    # 使用自定义分页类，支持通过URL参数设置每页数据量
    'DEFAULT_PAGINATION_CLASS': 'backend.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 100,
        },
        'KEY_PREFIX': 'fmrs',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
