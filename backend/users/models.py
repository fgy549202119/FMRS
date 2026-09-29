"""
用户管理模块 - 数据模型定义

该模块定义了设施管理与报修系统(FMRS)的用户相关数据模型，
包括普通用户、维修人员和管理员三种用户角色。

模型结构：
    User (普通用户)
        - 继承Django的AbstractUser，拥有完整的用户认证功能
        - 包含学生和教师两种用户类型
        - 用于提交报修请求、查看报修进度、评价服务等
    
    RepairStaff (维修人员)
        - 独立的用户模型，不继承AbstractUser
        - 用于接收和处理报修工单
        - 包含在线状态、当前工单数等维修相关属性
    
    Administrator (管理员)
        - 独立的用户模型，不继承AbstractUser
        - 用于系统管理、数据统计、人员管理等

设计说明：
    - 采用三种独立用户模型而非单一模型，便于不同角色的权限管理
    - User继承AbstractUser，可使用Django内置的认证系统
    - RepairStaff和Administrator独立管理，避免与Django认证系统耦合

作者：范广宇
创建日期：2026年
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    普通用户模型
    
    该模型继承自Django的AbstractUser，用于表示系统中的普通用户（学生和教师）。
    拥有Django内置的认证功能，包括密码加密、会话管理等。
    
    用户类型：
        - student: 学生用户，可提交报修请求
        - teacher: 教师用户，可提交报修请求
        - staff: 维修人员（仅用于User表标记，实际维修人员使用RepairStaff模型）
        - admin: 管理员（仅用于User表标记，实际管理员使用Administrator模型）
    
    继承自AbstractUser的字段：
        - username: 用户名（必填，唯一）
        - password: 密码（自动加密存储）
        - email: 邮箱
        - first_name, last_name: 姓名（本系统不使用）
        - is_active: 是否激活
        - is_staff: 是否为员工
        - is_superuser: 是否为超级用户
        - last_login: 最后登录时间
        - date_joined: 注册时间
    
    使用场景：
        - 用户注册和登录
        - 提交报修请求
        - 查看报修进度
        - 对维修服务进行评价
    """
    
    # 用户类型选项
    # 定义系统中支持的用户角色类型
    USER_TYPE_CHOICES = (
        ('student', '学生'),      # 学生用户
        ('teacher', '教师'),      # 教师用户
        ('staff', '维修人员'),    # 维修人员标记
        ('admin', '管理员'),      # 管理员标记
    )
    
    # 性别选项
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    
    # 用户类型字段
    # 用于区分不同角色的用户，默认为学生
    user_type = models.CharField('用户类型', max_length=20, choices=USER_TYPE_CHOICES, default='student')
    
    # 真实姓名字段
    # 用于显示用户的真实姓名，便于识别和联系
    real_name = models.CharField('真实姓名', max_length=50)
    
    # 性别字段
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES, default='male')
    
    # 头像字段
    # 存储头像图片的URL路径，可为空
    avatar = models.CharField('头像', max_length=500, blank=True, null=True)
    
    # 联系方式字段
    # 用于维修人员联系报修用户
    phone = models.CharField('联系方式', max_length=20, blank=True, null=True)
    
    # 学号/教师号/工号字段
    # 用于标识用户的身份编号，必须唯一
    user_no = models.CharField('学号/教师号/工号', max_length=50, blank=True, null=True, unique=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        ordering = ['id']
        
    def __str__(self):
        """
        返回用户的字符串表示
        
        格式：真实姓名(用户类型显示名)
        例如：张三(学生)
        
        返回值：
            str: 用户的字符串表示
        """
        return f"{self.real_name}({self.get_user_type_display()})"


class RepairStaff(models.Model):
    """
    维修人员模型
    
    该模型用于表示系统中的维修人员，独立于Django的认证系统。
    维修人员通过独立的账号体系管理，便于区分不同的登录入口。
    
    主要属性：
        - staff_no: 维修人员账号，用于登录
        - password: 密码（加密存储）
        - real_name: 真实姓名
        - status: 在岗状态（在线/离线/调休）
        - current_order_count: 当前处理中的工单数量
    
    使用场景：
        - 维修人员登录系统
        - 接收和处理报修工单
        - 记录维修过程和结果
        - 管理个人工作状态
    
    设计说明：
        - 不继承AbstractUser，使用独立的认证逻辑
        - 通过session存储登录状态
        - 包含工作状态管理，便于派单系统使用
    """
    
    # 性别选项
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    
    # 在岗状态选项
    # 用于派单系统判断是否可以分配新工单
    STATUS_CHOICES = (
        ('online', '在线'),      # 在线状态，可接收新工单
        ('offline', '离线'),     # 离线状态，不接收新工单
        ('leave', '调休'),       # 调休状态，暂时不接收工单
    )
    
    # 维修人员账号
    # 用于登录系统，必须唯一
    staff_no = models.CharField('维修人员账号', max_length=20, unique=True)
    
    # 密码字段
    # 存储加密后的密码，使用Django的密码哈希算法
    password = models.CharField('密码', max_length=128)
    
    # 真实姓名
    real_name = models.CharField('姓名', max_length=50)
    
    # 性别
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES, default='male')
    
    # 头像
    avatar = models.CharField('头像', max_length=500, blank=True, null=True)
    
    # 联系方式
    # 用于用户联系维修人员
    phone = models.CharField('联系方式', max_length=20)
    
    # 是否活跃
    # 用于控制账号是否可用
    is_active = models.BooleanField('是否活跃', default=True)
    
    # 是否在线
    # 用于实时显示在线状态
    is_online = models.BooleanField('是否在线', default=True)
    
    # 在岗状态
    # 用于派单系统判断是否可分配工单
    status = models.CharField('在岗状态', max_length=20, choices=STATUS_CHOICES, default='online')
    
    # 当前工单数
    # 记录正在处理中的工单数量，用于负载均衡
    current_order_count = models.IntegerField('当前工单数', default=0)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'repair_staff'
        verbose_name = '维修人员'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回维修人员的字符串表示
        
        格式：真实姓名(账号)
        例如：李四(staff001)
        
        返回值：
            str: 维修人员的字符串表示
        """
        return f"{self.real_name}({self.staff_no})"


class Administrator(models.Model):
    """
    管理员模型
    
    该模型用于表示系统中的管理员，独立于Django的认证系统。
    管理员拥有系统的最高权限，可以进行用户管理、数据统计等操作。
    
    主要权限：
        - 用户管理：查看、添加、修改、删除用户
        - 维修人员管理：管理维修人员信息
        - 设备管理：管理设备信息和设备类型
        - 报修管理：查看所有报修工单，进行统计分析
        - 系统设置：公告发布、知识库管理等
    
    使用场景：
        - 管理员登录后台系统
        - 用户和维修人员管理
        - 系统数据统计和分析
        - 公告和知识库管理
    
    设计说明：
        - 不继承AbstractUser，使用独立的认证逻辑
        - 通过session存储登录状态
        - 与Django admin后台分离，使用独立的管理界面
    """
    
    # 性别选项
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    
    # 管理员账号
    # 用于登录系统，必须唯一
    admin_no = models.CharField('管理员账号', max_length=20, unique=True)
    
    # 密码字段
    # 存储加密后的密码
    password = models.CharField('密码', max_length=128)
    
    # 真实姓名
    real_name = models.CharField('姓名', max_length=50)
    
    # 性别
    gender = models.CharField('性别', max_length=10, choices=GENDER_CHOICES, default='male')
    
    # 头像
    avatar = models.CharField('头像', max_length=500, blank=True, null=True)
    
    # 联系方式
    phone = models.CharField('联系方式', max_length=20)
    
    # 是否活跃
    is_active = models.BooleanField('是否活跃', default=True)
    
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    # 更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'administrator'
        verbose_name = '管理员'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        """
        返回管理员的字符串表示
        
        格式：真实姓名(账号)
        例如：王五(admin001)
        
        返回值：
            str: 管理员的字符串表示
        """
        return f"{self.real_name}({self.admin_no})"


import secrets


class AuthToken(models.Model):
    """
    统一认证令牌模型

    替代 Session 实现三端独立 Token 认证，解决同浏览器 Session 覆盖问题。
    每条记录存储一个 Token，关联 user_type + user_id 定位具体身份。
    """
    TOKEN_TYPE_CHOICES = (
        ('user', '用户'),
        ('staff', '维修人员'),
        ('admin', '管理员'),
    )

    key = models.CharField('Token', max_length=40, unique=True, db_index=True)
    user_type = models.CharField('用户类型', max_length=10, choices=TOKEN_TYPE_CHOICES)
    user_id = models.IntegerField('用户ID')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'auth_token'
        verbose_name = '认证令牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user_type}:{self.user_id} - {self.key[:8]}..."

    @classmethod
    def generate(cls, user_type, user_id):
        cls.objects.filter(user_type=user_type, user_id=user_id).delete()
        token = cls(key=secrets.token_hex(20), user_type=user_type, user_id=user_id)
        token.save()
        return token


class MessageBoard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='留言用户', related_name='messages')
    title = models.CharField('留言标题', max_length=200)
    content = models.TextField('留言内容')
    is_deleted = models.BooleanField('是否删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'message_board'
        verbose_name = '留言板'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'is_deleted'], name='idx_msg_user'),
            models.Index(fields=['-created_at'], name='idx_msg_created'),
        ]

    def __str__(self):
        return f'{self.user.real_name} - {self.title}'
