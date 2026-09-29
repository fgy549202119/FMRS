"""
报修管理模块 - 数据模型定义

该模块定义了设施管理与报修系统(FMRS)的核心业务模型，
包括报修工单、评价、转派记录、在线状态等。

模型结构：
    RepairOrder (报修工单)
        - 核心业务模型，记录完整的报修流程
        - 包含设备信息、位置信息、用户信息、维修人员信息等
        - 支持工单状态流转、审核、转派等功能
    
    TransferRecord (转派记录)
        - 记录工单转派历史
        - 支持管理员转派和维修人员申请转派
    
    StaffOnlineStatus (维修人员在线状态)
        - 记录维修人员的在线状态
        - 支持心跳检测机制
    
    Attachment (附件)
        - 存储工单相关的图片、文档等附件
    
    Evaluation (评价)
        - 用户对维修服务的评价
        - 支持多维度评分（质量、速度、态度）
    
    EvaluationAppeal (评价申诉)
        - 维修人员对评价的申诉
        - 支持管理员审核处理

工单状态流转：
    WAITING -> IN_PROGRESS -> PENDING_ADMIN_CLOSE -> CLOSED
                ↑                    ↓
                └── REJECTED ←──────┘

作者：范广宇
创建日期：2026年
"""

from django.db import models
from users.models import User, RepairStaff
from equipment.models import Equipment, EquipmentType
import random
import string
from django.utils import timezone


def generate_repair_no():
    """
    生成唯一的报修编号
    
    编号格式：RP + 日期(YYYYMMDD) + 6位随机字符
    例如：RP20240401ABC123
    
    返回值：
        str: 生成的报修编号
    """
    prefix = 'RP'
    date_str = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{date_str}{random_str}"


class RepairOrder(models.Model):
    """
    报修工单模型
    
    该模型是系统的核心业务模型，记录从用户提交报修到工单完成的完整流程。
    包含设备信息、位置信息、用户信息、维修人员信息、时间节点等。
    
    状态说明：
        - WAITING: 待接单，工单已创建等待维修人员接单
        - IN_PROGRESS: 维修中，维修人员已接单正在处理
        - PENDING_ADMIN_CLOSE: 待管理员审核，维修完成等待审核
        - CLOSED: 已完成，审核通过工单关闭
        - REJECTED: 已驳回，审核不通过退回重新处理
    
    字段分组：
        - 基本信息：报修编号、设备信息、故障描述
        - 位置信息：院区、楼栋、楼层、房间
        - 用户信息：报修用户、联系方式
        - 维修信息：维修人员、时间节点
        - 审核信息：审核人、审核回复
        - 状态信息：状态、删除标记、转派标记
    
    使用场景：
        - 用户提交报修请求
        - 维修人员接单和处理
        - 管理员审核和统计
    """
    
    # 工单状态选项
    STATUS_CHOICES = (
        ('WAITING', '待接单'),              # 初始状态，等待维修人员接单
        ('IN_PROGRESS', '维修中'),          # 维修人员已接单，正在处理
        ('PENDING_ADMIN_CLOSE', '待管理员审核'),  # 维修完成，等待管理员审核
        ('CLOSED', '已完成'),               # 审核通过，工单关闭
        ('REJECTED', '已驳回'),             # 审核不通过，退回重新处理
    )
    
    # 用户类型选项
    USER_TYPE_CHOICES = (
        ('teacher', '教职工'),
        ('student', '学生'),
    )
    
    # ========== 基本信息 ==========
    # 报修编号，自动生成，唯一标识
    repair_no = models.CharField('报修编号', max_length=50, unique=True, default=generate_repair_no)
    
    # 关联设备（可选）
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name='设备', null=True, blank=True)
    
    # 设备名称（冗余存储，便于查询和显示）
    equipment_name = models.CharField('设备名称', max_length=200)
    
    # 设备类型
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.SET_NULL, verbose_name='设备类型', null=True, blank=True)

    equipment_sequence_number = models.IntegerField('设备序号', blank=True, null=True)

    # 故障数量，用于统计设备故障次数
    fault_count = models.IntegerField('故障数量', default=1)
    
    # ========== 位置信息 ==========
    location = models.CharField('院区', max_length=50, blank=True, null=True)
    building = models.CharField('楼栋', max_length=100, blank=True, null=True)
    floor = models.CharField('楼层', max_length=20, blank=True, null=True)
    room = models.CharField('房间/教室', max_length=100, blank=True, null=True)
    location_detail = models.CharField('详细位置', max_length=255, blank=True, null=True)
    
    # 故障描述
    description = models.TextField('故障描述', blank=True, null=True)
    
    # ========== 用户信息 ==========
    # 报修用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='报修用户', related_name='repair_orders', null=True, blank=True)
    
    # 用户信息冗余字段（便于查询和防止用户删除后数据丢失）
    user_no = models.CharField('用户账号', max_length=50, blank=True, null=True)
    user_name = models.CharField('用户姓名', max_length=50, blank=True, null=True)
    user_type = models.CharField('用户类型', max_length=20, choices=USER_TYPE_CHOICES, default='student')
    user_phone = models.CharField('用户电话', max_length=20, blank=True, null=True)
    
    # ========== 状态信息 ==========
    status = models.CharField('状态', max_length=30, choices=STATUS_CHOICES, default='WAITING')

    # ========== 维修人员信息 ==========
    # 维修人员
    staff = models.ForeignKey(RepairStaff, on_delete=models.SET_NULL, verbose_name='维修人员', null=True, blank=True, related_name='repair_orders')
    
    # 维修人员信息冗余字段
    staff_no = models.CharField('维修人员账号', max_length=20, blank=True, null=True)
    staff_name = models.CharField('维修人员姓名', max_length=50, blank=True, null=True)
    
    # ========== 时间节点 ==========
    accept_time = models.DateTimeField('接单时间', blank=True, null=True)
    repair_start_time = models.DateTimeField('开始维修时间', blank=True, null=True)
    repair_end_time = models.DateTimeField('结束维修时间', blank=True, null=True)
    complete_time = models.DateTimeField('提交完成时间', blank=True, null=True)
    
    # ========== 审核信息 ==========
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='审核人', null=True, blank=True, related_name='reviewed_orders')
    review_reply = models.TextField('审核回复', blank=True, null=True)
    review_time = models.DateTimeField('审核时间', blank=True, null=True)
    
    # ========== 其他信息 ==========
    # 紧急标记（教师报修自动标记）
    is_urgent = models.BooleanField('是否紧急', default=False)
    # 实际耗时（分钟）
    actual_duration = models.FloatField('实际耗时(分钟)', blank=True, null=True)
    
    # 软删除标记
    is_deleted = models.BooleanField('是否删除', default=False)
    deleted_at = models.DateTimeField('删除时间', blank=True, null=True)
    
    # 转派标记
    is_transferred = models.BooleanField('是否已转派', default=False)
    
    # 现场照片
    scene_photo = models.TextField('现场照片', blank=True, null=True)
    
    # 维修说明
    remark = models.TextField('维修说明', blank=True, null=True)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'repair_repair_order'
        verbose_name = '报修工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_repair_status'),
            models.Index(fields=['-created_at'], name='idx_repair_created'),
            models.Index(fields=['user_id', 'is_deleted'], name='idx_repair_user'),
            models.Index(fields=['staff_id', 'status'], name='idx_repair_staff_status'),
            models.Index(fields=['is_deleted'], name='idx_repair_deleted'),
        ]
        
    def __str__(self):
        """
        返回工单的字符串表示
        
        格式：报修编号 - 设备名称
        例如：RP20240401ABC123 - 空调
        
        返回值：
            str: 工单的字符串表示
        """
        return f"{self.repair_no} - {self.equipment_name}"
    
    def save(self, *args, **kwargs):
        """
        重写保存方法，自动填充冗余字段
        
        在保存工单时自动：
        1. 生成报修编号（如果不存在）
        2. 从用户对象填充用户信息
        3. 从设备对象填充设备信息
        
        参数：
            *args: 位置参数
            **kwargs: 关键字参数
        """
        # 如果没有报修编号，自动生成
        if not self.repair_no:
            self.repair_no = generate_repair_no()
        
        # 从用户对象填充用户信息
        if self.user:
            self.user_no = self.user.user_no or self.user.username
            self.user_name = self.user.real_name or self.user.username
            self.user_phone = self.user.phone
            if not self.user_type:
                self.user_type = 'teacher' if hasattr(self.user, 'user_type') and self.user.user_type == 'teacher' else 'student'
        
        # 从设备对象填充设备信息
        if self.equipment:
            self.equipment_name = self.equipment.equipment_name
            self.equipment_type = self.equipment.equipment_type
        
        super().save(*args, **kwargs)
    
    def calculate_duration(self):
        """
        计算实际维修耗时
        
        根据开始维修时间和结束维修时间计算耗时（分钟）。
        
        返回值：
            float: 维修耗时（分钟），如果时间不完整则返回None
        """
        if self.repair_start_time and self.repair_end_time:
            delta = self.repair_end_time - self.repair_start_time
            self.actual_duration = delta.total_seconds() / 60
            return self.actual_duration
        return None


class TransferRecord(models.Model):
    """
    工单转派记录模型
    
    记录工单的转派历史，包括管理员转派和维修人员申请转派。
    
    转派类型：
        - admin: 管理员转派，管理员直接分配或重新分配工单
        - staff: 维修员申请，维修人员主动申请转派
    
    状态说明：
        - pending: 待审核，转派申请等待审核
        - approved: 已生效，转派已执行
        - rejected: 已拒绝，转派申请被拒绝
    
    使用场景：
        - 管理员重新分配工单
        - 维修人员因故无法处理申请转派
        - 工单转派历史查询
    """
    
    # 转派状态选项
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已生效'),
        ('rejected', '已拒绝'),
    )
    
    # 转派类型选项
    TRANSFER_TYPE_CHOICES = (
        ('admin', '管理员转派'),
        ('staff', '维修员申请'),
    )
    
    # 关联工单
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, verbose_name='工单', related_name='transfers')
    
    # 原维修人员
    from_staff = models.ForeignKey(RepairStaff, on_delete=models.SET_NULL, verbose_name='原维修人员', null=True, blank=True, related_name='transfers_from')
    
    # 目标维修人员
    to_staff = models.ForeignKey(RepairStaff, on_delete=models.SET_NULL, verbose_name='目标维修人员', null=True, blank=True, related_name='transfers_to')
    
    # 转派类型
    transfer_type = models.CharField('转派类型', max_length=20, choices=TRANSFER_TYPE_CHOICES, default='admin')
    
    # 转派原因
    reason = models.TextField('转派原因')
    
    # 审核状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='approved')
    
    # 审核人
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='审核人', null=True, blank=True, related_name='reviewed_transfers')
    
    # 审核回复
    review_reply = models.TextField('审核回复', blank=True, null=True)
    
    # 生效时间
    effective_time = models.DateTimeField('生效时间', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'transfer_record'
        verbose_name = '转派记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回转派记录的字符串表示
        
        格式：工单编号 - 原维修人员 → 目标维修人员
        
        返回值：
            str: 转派记录的字符串表示
        """
        return f"{self.order.repair_no} - {self.from_staff} → {self.to_staff}"


class StaffOnlineStatus(models.Model):
    """
    维修人员在线状态模型
    
    记录维修人员的实时在线状态，支持心跳检测机制。
    用于派单系统判断维修人员是否可接收新工单。
    
    心跳机制：
        - 维修人员定期发送心跳请求
        - 超过120秒未收到心跳则判定为离线
    
    使用场景：
        - 派单系统选择在线维修人员
        - 维修人员状态监控
        - 工作量统计
    """
    
    # 关联维修人员（一对一关系）
    staff = models.OneToOneField(RepairStaff, on_delete=models.CASCADE, verbose_name='维修人员', related_name='online_status')
    
    # 是否在线
    is_online = models.BooleanField('是否在线', default=False)
    
    # 最后心跳时间
    last_heartbeat = models.DateTimeField('最后心跳时间', blank=True, null=True)
    
    # 登录时间
    login_time = models.DateTimeField('登录时间', blank=True, null=True)
    
    # 登出时间
    logout_time = models.DateTimeField('登出时间', blank=True, null=True)
    
    # 所属院区
    campus = models.CharField('所属院区', max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'staff_online_status'
        verbose_name = '在线状态'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        """
        返回在线状态的字符串表示
        
        返回值：
            str: 维修人员姓名 - 在线/离线
        """
        return f"{self.staff.name} - {'在线' if self.is_online else '离线'}"
    
    @property
    def is_active(self):
        """
        判断维修人员是否活跃
        
        活跃条件：
        1. 在线状态为True
        2. 最后心跳时间存在
        3. 最后心跳时间在120秒内
        
        返回值：
            bool: 是否活跃
        """
        if not self.is_online:
            return False
        if not self.last_heartbeat:
            return False
        from django.utils import timezone as tz
        delta = tz.now() - self.last_heartbeat
        return delta.total_seconds() < 120


class Attachment(models.Model):
    """
    附件模型
    
    存储工单相关的附件信息，包括图片、文档、视频等。
    
    使用场景：
        - 报修时上传现场照片
        - 维修完成时上传维修照片
        - 存储相关文档资料
    """
    
    # 文件类型选项
    FILE_TYPE_CHOICES = (
        ('image', '图片'),
        ('document', '文档'),
        ('video', '视频'),
        ('other', '其他'),
    )
    
    # 关联工单
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, verbose_name='工单', related_name='attachments', null=True, blank=True)
    
    # 上传者
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='上传者', null=True, blank=True)
    
    # 文件名
    file_name = models.CharField('文件名', max_length=200)
    
    # 文件路径
    file_path = models.CharField('文件路径', max_length=500)
    
    # 文件大小（字节）
    file_size = models.IntegerField('文件大小(bytes)')
    
    # 文件类型
    file_type = models.CharField('文件类型', max_length=20, choices=FILE_TYPE_CHOICES, default='image')
    
    # MIME类型
    mime_type = models.CharField('MIME类型', max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField('上传时间', auto_now_add=True)
    
    class Meta:
        db_table = 'attachment'
        verbose_name = '附件'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回附件的字符串表示
        
        返回值：
            str: 文件名
        """
        return self.file_name


class Evaluation(models.Model):
    """
    评价模型
    
    用户对维修服务的评价，支持多维度评分。
    
    评分维度：
        - quality_rating: 维修质量评分（1-5星）
        - speed_rating: 响应速度评分（1-5星）
        - attitude_rating: 服务态度评分（1-5星）
        - rating: 综合评分（自动计算平均值）
    
    状态管理：
        - is_hidden: 是否隐藏（管理员可隐藏不当评价）
        - is_deleted: 是否删除（软删除）
        - is_reviewed: 是否已审核
    
    使用场景：
        - 用户对完成的工单进行评价
        - 管理员查看评价统计
        - 维修人员查看自己的评价
    """
    
    # 评分选项（1-5星）
    RATING_CHOICES = (
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    )
    
    # 关联工单
    order = models.ForeignKey(RepairOrder, on_delete=models.CASCADE, verbose_name='工单', related_name='evaluation', null=True, blank=True)
    
    # 评价用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评价用户', null=True, blank=True)
    user_name = models.CharField('用户姓名', max_length=50, blank=True, null=True)
    
    # 维修人员
    staff = models.ForeignKey(RepairStaff, on_delete=models.CASCADE, verbose_name='维修人员', null=True, blank=True)
    staff_name = models.CharField('维修人员姓名', max_length=50, blank=True, null=True)
    
    # 多维度评分
    quality_rating = models.IntegerField('维修质量评分', choices=RATING_CHOICES, default=5)
    speed_rating = models.IntegerField('响应速度评分', choices=RATING_CHOICES, default=5)
    attitude_rating = models.IntegerField('服务态度评分', choices=RATING_CHOICES, default=5)
    
    # 综合评分（自动计算）
    rating = models.IntegerField('综合评分', choices=RATING_CHOICES, default=5)
    
    # 评价内容
    content = models.TextField('评价内容', blank=True, null=True)
    
    # 状态管理
    is_hidden = models.BooleanField('是否隐藏', default=False)
    hidden_reason = models.CharField('隐藏原因', max_length=200, blank=True, null=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    is_reviewed = models.BooleanField('是否已审核', default=False)
    review_reply = models.TextField('审核回复', blank=True, null=True)
    reviewed_at = models.DateTimeField('审核时间', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'evaluation'
        verbose_name = '评价信息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回评价的字符串表示
        
        格式：工单编号 - N星评价
        
        返回值：
            str: 评价的字符串表示
        """
        repair_no = self.order.repair_no if self.order else '未知工单'
        return f"{repair_no} - {self.rating}星评价"
    
    def save(self, *args, **kwargs):
        """
        重写保存方法，自动计算综合评分
        
        综合评分 = (质量评分 + 速度评分 + 态度评分) / 3，四舍五入取整
        """
        avg = (self.quality_rating + self.speed_rating + self.attitude_rating) / 3
        self.rating = round(avg)
        super().save(*args, **kwargs)


class EvaluationAppeal(models.Model):
    """
    评价申诉模型
    
    维修人员对用户评价的申诉，由管理员审核处理。
    
    申诉规则：
        - 只能对3天内的评价进行申诉
        - 同一评价只能申诉一次
    
    状态说明：
        - pending: 待处理，申诉等待管理员处理
        - approved: 已通过，申诉成功
        - rejected: 已驳回，申诉失败
    
    使用场景：
        - 维修人员认为评价不公正时申诉
        - 管理员审核申诉
    """
    
    # 申诉状态选项
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
    )
    
    # 关联评价
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, verbose_name='评价', related_name='appeals')
    
    # 申诉人
    staff = models.ForeignKey(RepairStaff, on_delete=models.CASCADE, verbose_name='申诉人')
    staff_name = models.CharField('申诉人姓名', max_length=50, blank=True, null=True)
    
    # 申诉理由
    reason = models.TextField('申诉理由')
    
    # 证据材料
    evidence = models.TextField('证据材料', blank=True, null=True)
    
    # 处理状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 处理回复
    reply = models.TextField('处理回复', blank=True, null=True)
    
    # 处理人
    handler = models.CharField('处理人', max_length=50, blank=True, null=True)
    
    # 处理时间
    handle_time = models.DateTimeField('处理时间', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'evaluation_appeal'
        verbose_name = '评价申诉'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回申诉的字符串表示
        
        格式：申诉人姓名 - 评价申诉
        
        返回值：
            str: 申诉的字符串表示
        """
        return f"{self.staff_name} - 评价申诉"
