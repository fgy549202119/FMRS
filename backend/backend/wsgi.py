"""
WSGI应用入口配置

该模块是Django项目的WSGI(Web Server Gateway Interface)应用入口，
用于在生产环境中部署Django应用。

WSGI是Python Web应用与Web服务器之间的标准接口协议，
常见的支持WSGI的Web服务器包括：
- Gunicorn：Python WSGI HTTP服务器
- uWSGI：功能强大的应用服务器
- Apache + mod_wsgi：Apache的WSGI模块

工作原理：
    1. Web服务器加载该模块
    2. 获取application对象作为WSGI应用入口
    3. 将HTTP请求转发给application处理
    4. application处理请求并返回响应

部署示例（Gunicorn）：
    gunicorn backend.wsgi:application --bind 0.0.0.0:8000

作者：FMRS开发者-范广宇
创建日期：2026年
"""

import os

from django.core.wsgi import get_wsgi_application

# 设置Django配置模块
# 必须在导入Django应用之前设置，确保Django能正确加载配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 获取WSGI应用对象
# 该对象是WSGI服务器调用的入口点
# get_wsgi_application()会初始化Django并返回可调用的WSGI应用
application = get_wsgi_application()
