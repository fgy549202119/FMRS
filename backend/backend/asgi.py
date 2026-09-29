"""
ASGI应用入口配置

该模块是Django项目的ASGI(Asynchronous Server Gateway Interface)应用入口，
用于支持异步Web应用部署。

ASGI是WSGI的异步版本，支持：
- WebSocket连接：实时双向通信
- HTTP/2协议：新一代HTTP协议
- 异步视图：提高并发处理能力
- 后台任务：在请求处理过程中执行异步任务

与WSGI的区别：
    - WSGI是同步的，每个请求占用一个线程/进程
    - ASGI是异步的，可以在单个线程中处理多个请求

支持的ASGI服务器：
    - Daphne：Django Channels官方推荐
    - Uvicorn：高性能ASGI服务器
    - Hypercorn：支持HTTP/2的ASGI服务器

部署示例（Uvicorn）：
    uvicorn backend.asgi:application --host 0.0.0.0 --port 8000

作者：FMRS开发者范广宇
创建日期：2026年
"""

import os

from django.core.asgi import get_asgi_application

# 设置Django配置模块
# 必须在导入Django应用之前设置，确保Django能正确加载配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 获取ASGI应用对象
# 该对象是ASGI服务器调用的入口点
# get_asgi_application()会初始化Django并返回可调用的ASGI应用
application = get_asgi_application()
