from django.db import models
from django.db.models import Sum
from django.utils import timezone
from users.models import User
import random
import string


def generate_equipment_no():
    prefix = 'EQ'
    timestamp = ''.join(random.choices(string.digits, k=8))
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{suffix}"


class EquipmentType(models.Model):
    STATUS_CHOICES = (
        ('active', '启用'),
        ('inactive', '停用'),
    )

    type_name = models.CharField('设备类型名称', max_length=100, unique=True)
    type_code = models.CharField('类型编码', max_length=50, blank=True, null=True)
    icon = models.CharField('图标', max_length=200, blank=True, null=True)
    description = models.TextField('类型描述', blank=True, null=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'equipment_type'
        verbose_name = '设备类型'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.type_name


class EquipmentTypeRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )

    type_name = models.CharField('申请类型名称', max_length=100)
    description = models.TextField('类型描述', blank=True, null=True)
    reason = models.TextField('申请理由')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='申请人', related_name='type_requests')
    applicant_name = models.CharField('申请人姓名', max_length=50, blank=True, null=True)
    status = models.CharField('审核状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='审核人', null=True, blank=True, related_name='reviewed_type_requests')
    review_reply = models.TextField('审核回复', blank=True, null=True)
    review_time = models.DateTimeField('审核时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'equipment_type_request'
        verbose_name = '设备类型申请'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.applicant_name} - {self.type_name}"

    def save(self, *args, **kwargs):
        if self.applicant:
            self.applicant_name = self.applicant.real_name or self.applicant.username
        super().save(*args, **kwargs)


class Equipment(models.Model):
    STATUS_CHOICES = (
        ('正常', '正常'),
        ('故障', '故障'),
    )

    sequence_number = models.IntegerField('设备序号', unique=True, blank=True, null=True)
    equipment_no = models.CharField('设备编号', max_length=50, unique=True, default=generate_equipment_no)
    equipment_name = models.CharField('设备名称', max_length=200)
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, verbose_name='设备类型')
    equipment_image = models.TextField('设备图片', blank=True, null=True)
    specification = models.CharField('设备规格', max_length=200, blank=True, null=True)
    fault_count = models.IntegerField('故障数量', default=0)
    status = models.CharField('设备状态', max_length=50, choices=STATUS_CHOICES, default='正常')
    is_reportable = models.BooleanField('可报修', default=True)
    supplier = models.CharField('供货商', max_length=255, blank=True, default='')
    building = models.ForeignKey('location.Building', on_delete=models.SET_NULL, verbose_name='所在楼栋', null=True, blank=True)
    floor = models.ForeignKey('location.Floor', on_delete=models.SET_NULL, verbose_name='所在楼层', null=True, blank=True)
    room = models.ForeignKey('location.Room', on_delete=models.SET_NULL, verbose_name='所在房间', null=True, blank=True)
    publish_time = models.DateTimeField('发布时间', auto_now_add=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'equipment'
        verbose_name = '公共设备'
        verbose_name_plural = verbose_name
        ordering = ['sequence_number']
        indexes = [
            models.Index(fields=['building'], name='idx_equip_building'),
            models.Index(fields=['equipment_type'], name='idx_equip_type'),
            models.Index(fields=['fault_count'], name='idx_equip_fault'),
            models.Index(fields=['building', 'equipment_type'], name='idx_equip_building_type'),
            models.Index(fields=['equipment_name', 'building'], name='idx_equip_name_building'),
            models.Index(fields=['status'], name='idx_equip_status'),
        ]

    def __str__(self):
        return f"{self.sequence_number} - {self.equipment_name}"

    def save(self, *args, **kwargs):
        if not self.equipment_no:
            self.equipment_no = generate_equipment_no()
        if self.sequence_number is None:
            self.sequence_number = self._get_next_sequence_number()
        if self.fault_count > 0:
            self.status = '故障'
        else:
            self.status = '正常'
        super().save(*args, **kwargs)

    @classmethod
    def _get_next_sequence_number(cls):
        used_numbers = set(cls.objects.exclude(sequence_number__isnull=True).values_list('sequence_number', flat=True))
        if not used_numbers:
            return 1
        max_num = max(used_numbers)
        for i in range(1, max_num + 1):
            if i not in used_numbers:
                return i
        return max_num + 1

    @classmethod
    def recalculate_fault_count(cls, equipment_id):
        from repair.models import RepairOrder
        unfinished_statuses = ['WAITING', 'IN_PROGRESS', 'PENDING_ADMIN_CLOSE']
        result = RepairOrder.objects.filter(
            equipment_id=equipment_id,
            status__in=unfinished_statuses,
            is_deleted=False
        ).aggregate(total=Sum('fault_count'))
        fault_count = result['total'] or 0
        try:
            equip = cls.objects.get(id=equipment_id)
            equip.fault_count = fault_count
            equip.save()
        except cls.DoesNotExist:
            pass
