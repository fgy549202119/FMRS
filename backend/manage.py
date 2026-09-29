#!/usr/bin/env python
"""
Django命令行管理工具入口

该脚本是Django项目的命令行入口点，用于执行各种管理任务。
通过该脚本可以运行开发服务器、执行数据库迁移、创建应用等。

常用命令：
    python manage.py runserver          # 启动开发服务器
    python manage.py makemigrations     # 创建数据库迁移文件
    python manage.py migrate            # 执行数据库迁移
    python manage.py createsuperuser    # 创建超级管理员
    python manage.py collectstatic      # 收集静态文件
    python manage.py shell              # 进入Django Shell

工作原理：
    1. 设置DJANGO_SETTINGS_MODULE环境变量，指向项目配置文件
    2. 导入Django的核心管理模块
    3. 将命令行参数传递给execute_from_command_line执行

作者：FMRS开发者范广宇
创建日期：2026年
"""
import os
import sys


def main():
    """
    Django管理任务主函数
    
    该函数是manage.py脚本的入口点，负责：
    1. 设置默认的Django配置模块
    2. 导入并执行Django命令行工具
    3. 处理可能的导入错误
    
    执行流程：
        - os.environ.setdefault() 设置环境变量，确保Django能找到配置文件
        - execute_from_command_line() 解析sys.argv并执行对应的管理命令
        
    异常处理：
        如果Django未安装或不在Python路径中，会抛出ImportError，
        提示用户检查Django安装和虚拟环境状态。
    """
    # 设置Django配置模块
    # 指定使用backend目录下的settings.py作为项目配置文件
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    
    try:
        # 尝试导入Django的命令行执行函数
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # 导入失败时抛出详细的错误信息
        # 帮助用户诊断问题：Django未安装、路径问题或虚拟环境未激活
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 执行命令行任务
    # sys.argv包含命令行参数，如 ['manage.py', 'runserver', '8000']
    execute_from_command_line(sys.argv)


# Python脚本入口点
# 当直接运行manage.py时执行main函数
if __name__ == '__main__':
    main()
