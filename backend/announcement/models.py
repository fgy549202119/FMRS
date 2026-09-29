"""
公告管理模块 - 数据模型定义

该模块定义了设施管理与报修系统(FMRS)的公告相关数据模型。

模型结构：
    Announcement (校园公告)
        - 系统公告的发布和管理
        - 支持图片附件

使用场景：
    - 发布系统通知
    - 发布维修公告
    - 发布校园新闻

作者：范广宇
创建日期：2026年
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Announcement(models.Model):
    """
    校园公告模型
    
    该模型用于管理系统公告信息。
    
    主要属性：
        - title: 公告标题
        - content: 公告内容
        - image: 公告图片
        - publisher: 发布人
        - publish_time: 发布时间
    
    使用场景：
        - 发布系统公告
        - 发布维修通知
        - 公告列表展示
    """
    
    # 公告标题
    title = models.CharField('标题', max_length=200)
    
    # 公告内容
    content = models.TextField('内容')
    
    # 公告图片
    image = models.CharField('图片', max_length=500, blank=True, null=True)
    
    # 发布人
    publisher = models.CharField('发布人', max_length=50)
    
    # 发布时间
    publish_time = models.DateTimeField('发布时间', auto_now_add=True)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'announcement'
        verbose_name = '校园公告'
        verbose_name_plural = verbose_name
        ordering = ['-publish_time']

    def __str__(self):
        """
        返回公告的字符串表示
        
        返回值：
            str: 公告标题
        """
        return self.title
