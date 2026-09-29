"""
公共模块 - 数据模型定义

该模块定义了设施管理与报修系统(FMRS)的公共功能数据模型，
包括备件管理、维修日志、知识库等。

模型结构：
    SparePart (备件信息)
        - 备件库存管理
        - 支持入库、出库、调整操作
    
    SparePartRecord (备件记录)
        - 备件出入库记录
        - 追踪库存变动历史
    
    RepairLog (维修日志)
        - 维修过程中的日志记录
        - 支持图片附件
    
    RepairSparePart (维修备件使用)
        - 记录维修中使用的备件
        - 关联工单和备件
    
    KnowledgeBase (维修知识库)
        - 维修经验分享
        - 问题解决方案库

作者：范广宇
创建日期：2026年
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import User, RepairStaff
from equipment.models import EquipmentType


class SparePart(models.Model):
    """
    备件信息模型
    
    该模型用于管理维修备件的库存信息。
    支持入库、出库、库存预警等功能。
    
    主要属性：
        - part_no: 备件编号（唯一标识）
        - name: 备件名称
        - specification: 规格型号
        - brand: 品牌
        - unit: 单位（个/件/套/米/公斤/升）
        - quantity: 库存数量
        - unit_price: 单价
        - storage_location: 存放位置
    
    使用场景：
        - 备件入库登记
        - 维修时查询备件
        - 库存预警管理
    """
    
    # 单位选项
    UNIT_CHOICES = (
        ('个', '个'),
        ('件', '件'),
        ('套', '套'),
        ('米', '米'),
        ('公斤', '公斤'),
        ('升', '升'),
    )
    
    # 备件编号，唯一标识
    part_no = models.CharField('备件编号', max_length=50, unique=True)
    
    # 备件名称
    name = models.CharField('备件名称', max_length=200)
    
    # 规格型号
    specification = models.CharField('规格型号', max_length=200, blank=True)
    
    # 品牌
    brand = models.CharField('品牌', max_length=100, blank=True)
    
    # 单位
    unit = models.CharField('单位', max_length=20, choices=UNIT_CHOICES, default='个')
    
    # 存放位置
    storage_location = models.CharField('存放位置', max_length=200, blank=True)

    # 库存数量
    quantity = models.IntegerField('库存数量', default=0)
    
    # 单价
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    
    # 备注
    remark = models.TextField('备注', blank=True)

    # 供货商
    supplier = models.CharField('供货商', max_length=255, blank=True, default='')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'spare_part'
        verbose_name = '备件信息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        """
        返回备件的字符串表示
        
        格式：备件编号 - 备件名称
        
        返回值：
            str: 备件的字符串表示
        """
        return f"{self.part_no} - {self.name}"
    
    @property
    def is_low_stock(self):
        """
        判断是否库存不足
        
        当前实现为库存<=0时返回True。
        可根据需要添加安全库存字段。
        
        返回值：
            bool: 是否库存不足
        """
        return self.quantity <= 0


class SparePartRecord(models.Model):
    """
    备件记录模型
    
    该模型用于记录备件的出入库历史，追踪库存变动。
    
    主要属性：
        - part: 关联的备件
        - record_type: 记录类型（入库/出库/调整）
        - quantity: 变动数量
        - before_quantity: 变动前库存
        - after_quantity: 变动后库存
        - related_order_no: 关联单号
        - operator: 操作人
    
    使用场景：
        - 备件出入库记录查询
        - 库存变动审计
    """
    
    # 记录类型选项
    TYPE_CHOICES = (
        ('in', '入库'),       # 入库记录
        ('out', '出库'),      # 出库记录
        ('adjust', '调整'),   # 库存调整
    )
    
    # 关联备件
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='records', verbose_name='备件')
    
    # 记录类型
    record_type = models.CharField('记录类型', max_length=20, choices=TYPE_CHOICES)
    
    # 变动数量
    quantity = models.IntegerField('数量')
    
    # 变动前库存
    before_quantity = models.IntegerField('变动前库存')
    
    # 变动后库存
    after_quantity = models.IntegerField('变动后库存')
    
    # 关联单号（如工单编号）
    related_order_no = models.CharField('关联单号', max_length=50, blank=True)
    
    # 操作人
    operator = models.CharField('操作人', max_length=50)
    
    # 备注
    remark = models.TextField('备注', blank=True)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'spare_part_record'
        verbose_name = '备件记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class RepairLog(models.Model):
    """
    维修日志模型
    
    该模型用于记录维修过程中的日志信息，支持图片附件。
    
    主要属性：
        - repair_order: 关联的工单
        - content: 日志内容
        - images: 图片列表（JSON格式）
        - operator_no: 操作人账号
        - operator_name: 操作人姓名
    
    使用场景：
        - 维修过程记录
        - 问题追踪
        - 维修经验积累
    """
    
    # 关联工单
    repair_order = models.ForeignKey('repair.RepairOrder', on_delete=models.CASCADE, related_name='logs', verbose_name='工单')
    
    # 日志内容
    content = models.TextField('日志内容')
    
    # 图片列表（JSON格式存储）
    images = models.JSONField('图片列表', default=list, blank=True)
    
    # 操作人账号
    operator_no = models.CharField('操作人账号', max_length=50)
    
    # 操作人姓名
    operator_name = models.CharField('操作人姓名', max_length=50)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'repair_log'
        verbose_name = '维修日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        """
        返回维修日志的字符串表示
        
        格式：工单编号 - 日志
        
        返回值：
            str: 维修日志的字符串表示
        """
        return f"{self.repair_order.repair_no} - 日志"


class RepairSparePart(models.Model):
    """
    维修备件使用模型
    
    该模型用于记录维修过程中使用的备件信息。
    
    主要属性：
        - repair_order: 关联的工单
        - spare_part: 使用的备件
        - quantity: 使用数量
        - unit_price: 单价
        - total_price: 总价（自动计算）
    
    使用场景：
        - 记录维修使用的备件
        - 计算维修成本
        - 备件消耗统计
    """
    
    # 关联工单
    repair_order = models.ForeignKey('repair.RepairOrder', on_delete=models.CASCADE, related_name='used_parts', verbose_name='工单')
    
    # 使用的备件
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='used_in_repairs', verbose_name='备件')
    
    # 使用数量
    quantity = models.IntegerField('使用数量')
    
    # 单价
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    
    # 总价（自动计算）
    total_price = models.DecimalField('总价', max_digits=10, decimal_places=2)
    
    # 备注
    remark = models.CharField('备注', max_length=200, blank=True)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'repair_spare_part'
        verbose_name = '维修备件使用'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """
        重写保存方法，自动计算总价
        
        总价 = 使用数量 × 单价
        
        参数：
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if self.quantity is not None and self.unit_price is not None:
            self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class KnowledgeBase(models.Model):
    """
    维修知识库模型
    
    该模型用于存储维修经验和解决方案，形成知识库。
    
    主要属性：
        - title: 标题
        - category: 分类（电气/机械/管道/暖通/其他）
        - problem_description: 问题描述
        - solution: 解决方案
        - equipment_type: 设备类型
        - keywords: 关键词
        - view_count: 浏览次数
        - useful_count: 有用次数
    
    使用场景：
        - 维修经验分享
        - 问题解决方案查询
        - 维修知识积累
    """
    
    # 标题
    title = models.CharField('标题', max_length=200)
    
    # 问题描述
    problem_description = models.TextField('问题描述')
    
    # 解决方案
    solution = models.TextField('解决方案')
    
    # 设备类型
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.SET_NULL, verbose_name='设备类型', null=True, blank=True)
    
    # 关键词（逗号分隔）
    keywords = models.CharField('关键词', max_length=500, blank=True, help_text='逗号分隔')
    
    # 图片列表（JSON格式存储）
    images = models.JSONField('图片列表', default=list, blank=True)
    
    # 浏览次数
    view_count = models.IntegerField('浏览次数', default=0)
    
    # 有用次数
    useful_count = models.IntegerField('有用次数', default=0)
    
    # 作者
    author = models.CharField('作者', max_length=50)
    
    # 是否发布
    is_published = models.BooleanField('是否发布', default=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'knowledge_base'
        verbose_name = '维修知识库'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        """
        返回知识库条目的字符串表示
        
        返回值：
            str: 标题
        """
        return self.title
