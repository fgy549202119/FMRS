"""
文件上传视图模块

该模块提供了统一的文件上传接口，用于处理系统中各类图片的上传需求。
支持的上传类型包括：
- 头像上传（avatar）：用户个人头像
- 公告图片上传（announcement）：系统公告配图
- 设备图片上传（equipment）：设备信息图片
- 巡检图片上传（inspection）：巡检记录图片
- 报修图片上传（repair）：报修工单图片（默认）

主要功能：
- 接收前端上传的文件数据
- 验证文件格式（支持jpg、jpeg、png、gif、webp）
- 生成唯一文件名，防止文件名冲突
- 根据上传类型分类存储文件
- 返回文件访问URL

安全措施：
- 使用@csrf_exempt跳过CSRF验证（前后端分离架构）
- 限制上传文件格式，防止恶意文件上传
- 使用UUID生成文件名，防止路径遍历攻击

作者：FMRS开发者-范广宇
创建日期：2026年
"""

import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from datetime import datetime
import uuid


@csrf_exempt
@require_POST
def upload_image(request):
    """
    统一图片上传接口
    
    该视图函数处理所有类型的图片上传请求，支持多种上传场景。
    通过POST参数type区分不同的上传类型，将文件存储到对应目录。
    
    请求方式：
        POST /api/upload/
        
    请求参数：
        - file/image/avatar: 上传的文件对象（三选一）
        - type: 上传类型，可选值：avatar/announcement/equipment/inspection/repair
        
    返回格式：
        成功：{
            'code': 200,
            'message': '上传成功',
            'url': '/media/类型/文件名',
            'filename': '文件名'
        }
        失败：{'error': '错误信息'}
        
    处理流程：
        1. 检查请求中是否包含文件数据
        2. 验证文件格式是否合法
        3. 生成唯一文件名（日期_UUID.扩展名）
        4. 根据上传类型确定存储目录
        5. 保存文件到服务器
        6. 返回文件访问URL
        
    参数：
        request: Django HttpRequest对象
        
    返回值：
        JsonResponse: 包含上传结果的JSON响应
    """
    try:
        # 检查请求中是否包含文件数据
        # 支持多种字段名：file、image、avatar，兼容不同的前端实现
        if 'file' not in request.FILES and 'image' not in request.FILES and 'avatar' not in request.FILES:
            return JsonResponse({'error': '没有上传文件'}, status=400)
        
        # 获取上传的文件对象
        # 使用or操作符依次尝试不同的字段名
        file = request.FILES.get('file') or request.FILES.get('image') or request.FILES.get('avatar')
        
        # 验证文件对象是否有效
        if not file:
            return JsonResponse({'error': '文件为空'}, status=400)
        
        # 提取文件扩展名
        ext = os.path.splitext(file.name)[1]
        
        # 验证文件格式
        # 只允许常见的图片格式，防止上传恶意文件
        if ext.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return JsonResponse({'error': '不支持的文件格式'}, status=400)
        
        # 生成唯一文件名
        # 格式：日期_8位UUID.扩展名
        # 例如：20240401_a1b2c3d4.jpg
        filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 根据上传类型确定存储目录
        upload_type = request.POST.get('type', 'repair')
        if upload_type == 'avatar':
            # 用户头像存储目录
            save_dir = os.path.join(settings.MEDIA_ROOT, 'avatar')
        elif upload_type == 'announcement':
            # 公告图片存储目录
            save_dir = os.path.join(settings.MEDIA_ROOT, 'announcement')
        elif upload_type == 'equipment':
            # 设备图片存储目录
            save_dir = os.path.join(settings.MEDIA_ROOT, 'equipment')
        elif upload_type == 'inspection':
            # 巡检图片存储目录
            save_dir = os.path.join(settings.MEDIA_ROOT, 'inspection')
        else:
            # 报修图片存储目录（默认）
            save_dir = os.path.join(settings.MEDIA_ROOT, 'repair')
        
        # 创建存储目录
        # exist_ok=True 表示目录已存在时不抛出异常
        os.makedirs(save_dir, exist_ok=True)
        
        # 构建完整文件路径
        filepath = os.path.join(save_dir, filename)
        
        # 保存文件到服务器
        # 使用chunks()方法分块读取，适合大文件上传
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # 构建文件访问URL
        # 格式：/media/类型/文件名
        url = f"{settings.MEDIA_URL}{upload_type}/{filename}"
        
        # 返回成功响应
        return JsonResponse({
            'code': 200,
            'message': '上传成功',
            'url': url,
            'filename': filename
        })
    
    except Exception as e:
        # 捕获并返回异常信息
        # 生产环境应记录日志，避免直接返回错误详情
        return JsonResponse({'error': str(e)}, status=500)
