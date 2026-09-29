"""
巡检管理模块 - 数据模型定义

该模块定义了设施管理与报修系统(FMRS)的巡检相关数据模型，
包括巡检单和巡检记录。

模型结构：
    Inspection (巡检单)
        - 设备巡检的主记录
        - 包含位置信息、巡检结果、审核状态等
        - 支持审核驳回后自动生成报修工单
    
    InspectionRecord (巡检记录)
        - 巡检单的明细记录
        - 记录每个检查项目的状态

巡检流程：
    1. 维修人员创建巡检单
    2. 记录各检查项目状态
    3. 提交审核
    4. 管理员审核（通过/驳回）
    5. 驳回时可自动生成报修工单

作者：范广宇
创建日期：2026年
"""

from django.db import models
from users.models import RepairStaff
from equipment.models import EquipmentType, Equipment
from location.models import Campus, Building, Floor
import random
import string
from django.utils import timezone


def generate_inspection_no():
    """
    生成唯一的巡检单号
    
    编号格式：IN + 日期(YYYYMMDD) + 6位随机字符
    例如：IN20240401ABC123
    
    返回值：
        str: 生成的巡检单号
    """
    prefix = 'IN'
    date_str = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{date_str}{random_str}"


class Inspection(models.Model):
    """
    巡检单模型
    
    该模型用于记录设备巡检的完整信息，包括位置、结果、审核等。
    
    主要属性：
        - inspection_no: 巡检单号（自动生成）
        - equipment_type: 设备类型
        - 位置信息：校区、楼栋、楼层、房间号
        - result: 巡检结果（正常/异常）
        - status: 审核状态（待审核/已通过/已驳回）
        - staff: 巡检人员
    
    审核状态：
        - pending: 待审核
        - approved: 已通过
        - rejected: 已驳回（自动生成报修工单）
    
    使用场景：
        - 维修人员提交巡检记录
        - 管理员审核巡检结果
        - 异常情况自动转报修
    """
    
    # 审核状态选项
    STATUS_CHOICES = (
        ('pending', '待审核'),      # 等待管理员审核
        ('approved', '已通过'),     # 审核通过
        ('rejected', '已驳回'),     # 审核驳回，生成报修工单
    )

    # 巡检结果选项
    RESULT_CHOICES = (
        ('normal', '正常'),         # 设备运行正常
        ('abnormal', '异常'),       # 发现异常问题
    )
    
    # 巡检单号，自动生成，唯一标识
    inspection_no = models.CharField('巡检单号', max_length=50, unique=True, default=generate_inspection_no)
    
    # 设备
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name='设备', null=True, blank=True)
    equipment_sequence_number = models.IntegerField('设备序号', blank=True, null=True)
    
    # 位置信息
    campus = models.ForeignKey(Campus, on_delete=models.SET_NULL, verbose_name='院区', null=True, blank=True)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, verbose_name='楼栋', null=True, blank=True)
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, verbose_name='楼层', null=True, blank=True)
    room_number = models.CharField('房间号', max_length=50, blank=True, default='')
    location_detail = models.CharField('详细位置', max_length=200, blank=True, default='')
    
    # 自动生成的位置字符串
    location = models.CharField('设备位置', max_length=200, blank=True, default='')
    
    # 现场照片
    scene_photo = models.TextField('现场照片', blank=True, null=True)
    
    # 巡检结果
    result = models.CharField('巡检结果', max_length=20, choices=RESULT_CHOICES, default='normal')
    
    inspection_count = models.IntegerField('巡检数量', default=1)
    
    # 巡检记录/备注
    remark = models.TextField('巡检记录', blank=True, default='')
    
    # 巡检时间
    inspection_time = models.DateTimeField('巡检时间', default=timezone.now)
    
    # 巡检人员信息
    staff = models.ForeignKey(RepairStaff, on_delete=models.CASCADE, verbose_name='巡检人员')
    staff_no = models.CharField('巡检人员账号', max_length=20)
    staff_name = models.CharField('巡检人员姓名', max_length=50)
    
    # 巡检描述
    description = models.TextField('巡检描述', blank=True, null=True)
    
    # 审核状态
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 审核回复
    review_reply = models.TextField('审核回复', blank=True, null=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'inspection'
        verbose_name = '设备巡检'
        verbose_name_plural = verbose_name
        ordering = ['-inspection_time']
        indexes = [
            models.Index(fields=['status'], name='idx_inspection_status'),
            models.Index(fields=['staff_id'], name='idx_inspection_staff'),
            models.Index(fields=['-inspection_time'], name='idx_inspection_time'),
        ]
        
    def __str__(self):
        """
        返回巡检单的字符串表示
        
        格式：巡检单号 - 巡检人员姓名
        
        返回值：
            str: 巡检单的字符串表示
        """
        return f"{self.inspection_no} - {self.staff_name}"
    
    def save(self, *args, **kwargs):
        """
        重写保存方法，自动处理巡检单号和位置信息
        
        处理逻辑：
        1. 自动生成巡检单号
        2. 从维修人员对象填充账号和姓名
        3. 自动拼接位置信息字符串
        
        参数：
            *args: 位置参数
            **kwargs: 关键字参数
        """
        # 自动生成巡检单号
        if not self.inspection_no:
            self.inspection_no = generate_inspection_no()
        
        # 从维修人员对象填充信息
        if self.staff:
            self.staff_no = self.staff.staff_no
            self.staff_name = self.staff.real_name
        
        # 自动拼接位置信息
        location_parts = []
        if self.campus:
            location_parts.append(self.campus.name)
        if self.building:
            location_parts.append(self.building.name)
        if self.floor:
            location_parts.append(f'{self.floor.floor_number}层')
        if self.room_number:
            location_parts.append(self.room_number)
        if self.location_detail:
            location_parts.append(self.location_detail)
        self.location = ' '.join(location_parts)
        
        super().save(*args, **kwargs)


class InspectionRecord(models.Model):
    """
    巡检记录模型
    
    该模型用于记录巡检单中每个检查项目的详细状态。
    一个巡检单可以包含多条巡检记录。
    
    主要属性：
        - inspection: 关联的巡检单
        - item_name: 检查项目名称
        - item_status: 检查状态
        - remark: 备注
    
    使用场景：
        - 记录设备各项指标的检查结果
        - 如：电源状态、运行状态、清洁情况等
    """
    
    # 关联巡检单
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, verbose_name='巡检单', related_name='records')
    
    # 检查项目名称
    item_name = models.CharField('检查项目', max_length=200)
    
    # 检查状态
    item_status = models.CharField('检查状态', max_length=50)
    
    # 备注
    remark = models.TextField('备注', blank=True, null=True)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'inspection_record'
        verbose_name = '巡检记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回巡检记录的字符串表示
        
        格式：巡检单号 - 检查项目名称
        
        返回值：
            str: 巡检记录的字符串表示
        """
        return f"{self.inspection.inspection_no} - {self.item_name}"
