"""
用户管理模块 - 序列化器定义

该模块定义了用户相关模型的序列化器，用于：
- 将模型实例转换为JSON格式的响应数据
- 将请求数据反序列化为模型实例
- 数据验证和密码加密处理

序列化器结构：
    UserSerializer
        - 用户信息的序列化和反序列化
        - 密码更新时的加密处理
    
    UserRegisterSerializer
        - 用户注册专用序列化器
        - 包含确认密码验证
        - 自动创建用户并加密密码
    
    RepairStaffSerializer
        - 维修人员信息的序列化和反序列化
        - 密码创建和更新时的加密处理
    
    RepairStaffRegisterSerializer
        - 维修人员注册专用序列化器
        - 包含确认密码验证
    
    AdministratorSerializer
        - 管理员信息的序列化和反序列化

作者：范广宇
创建日期：2026年
"""

from rest_framework import serializers
from .models import User, RepairStaff, Administrator, MessageBoard
from django.contrib.auth.hashers import make_password
import re


def validate_phone(value):
    if not value:
        raise serializers.ValidationError('请输入联系方式')
    if not re.match(r'^1\d{10}$', value):
        raise serializers.ValidationError('手机号格式不正确')
    return value


def validate_password_strength(value):
    if not value:
        raise serializers.ValidationError('请输入密码')
    if len(value) < 6:
        raise serializers.ValidationError('密码长度不能少于6位')
    if not re.search(r'[a-z]', value):
        raise serializers.ValidationError('密码必须包含小写字母')
    if not re.search(r'[A-Z]', value):
        raise serializers.ValidationError('密码必须包含大写字母')
    if not re.search(r'\d', value):
        raise serializers.ValidationError('密码必须包含数字')
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]', value):
        raise serializers.ValidationError('密码必须包含特殊符号')
    return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'validators': [validate_password_strength]},
            'username': {'required': False},
            'phone': {'validators': [validate_phone]}
        }
    
    def update(self, instance, validated_data):
        """
        重写更新方法，处理密码加密
        
        当更新数据中包含密码时，使用Django的set_password方法
        进行加密，而不是直接存储明文密码。
        
        参数：
            instance: 要更新的用户实例
            validated_data: 验证后的数据字典
            
        返回值：
            User: 更新后的用户实例
            
        处理流程：
            1. 检查是否包含密码字段
            2. 如果包含密码，使用set_password加密
            3. 从validated_data中移除密码字段
            4. 调用父类的update方法更新其他字段
        """
        if 'password' in validated_data and validated_data['password']:
            # 使用Django的密码加密方法
            instance.set_password(validated_data['password'])
            validated_data.pop('password')
        
        return super().update(instance, validated_data)


class MessageBoardSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.real_name', default='')

    class Meta:
        model = MessageBoard
        fields = ['id', 'user', 'user_name', 'title', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user']


class UserRegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'real_name',
                  'gender', 'avatar', 'phone', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
            'phone': {'validators': [validate_phone]}
        }

    def validate(self, data):
        """
        自定义验证方法

        验证密码和确认密码是否一致。

        参数：
            data: 待验证的数据字典

        返回值：
            dict: 验证通过的数据

        异常：
            ValidationError: 两次密码不一致时抛出
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('两次密码不一致')
        return data

    def create(self, validated_data):
        """
        重写创建方法，处理用户创建

        创建用户时：
        1. 移除确认密码字段
        2. 将username（账号）复制给user_no（学号/教师号/工号）
        3. 使用create_user方法创建用户（自动加密密码）

        参数：
            validated_data: 验证后的数据字典

        返回值：
            User: 新创建的用户实例
        """
        # 移除确认密码字段
        validated_data.pop('confirm_password')

        # 将账号复制为用户编号
        validated_data['user_no'] = validated_data['username']

        # 使用create_user方法创建用户，密码会自动加密
        user = User.objects.create_user(**validated_data)
        return user


class RepairStaffSerializer(serializers.ModelSerializer):
    
    current_order_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RepairStaff
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'validators': [validate_password_strength]},
            'phone': {'validators': [validate_phone]}
        }
    
    def get_current_order_count(self, obj):
        from repair.models import RepairOrder
        return RepairOrder.objects.filter(
            staff_id=obj.id,
            status__in=['IN_PROGRESS', 'PENDING_ADMIN_CLOSE'],
            is_deleted=False
        ).count()
    
    def create(self, validated_data):
        """
        重写创建方法，处理密码加密
        
        创建维修人员时，对密码进行加密处理。
        
        参数：
            validated_data: 验证后的数据字典
            
        返回值：
            RepairStaff: 新创建的维修人员实例
        """
        if 'password' in validated_data:
            from django.contrib.auth.hashers import make_password
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        重写更新方法，处理密码加密
        
        更新维修人员信息时，如果包含密码字段则进行加密。
        
        参数：
            instance: 要更新的维修人员实例
            validated_data: 验证后的数据字典
            
        返回值：
            RepairStaff: 更新后的维修人员实例
        """
        if 'password' in validated_data and validated_data['password']:
            from django.contrib.auth.hashers import make_password
            instance.password = make_password(validated_data['password'])
            validated_data.pop('password')
        return super().update(instance, validated_data)


class RepairStaffRegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = RepairStaff
        fields = ['staff_no', 'password', 'confirm_password', 'real_name', 
                  'gender', 'avatar', 'phone']
        extra_kwargs = {
            'password': {'write_only': True},
            'phone': {'validators': [validate_phone]}
        }
    
    def validate(self, data):
        """
        验证密码和确认密码是否一致
        
        参数：
            data: 待验证的数据字典
            
        返回值：
            dict: 验证通过的数据
            
        异常：
            ValidationError: 两次密码不一致时抛出
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('两次密码不一致')
        return data
    
    def create(self, validated_data):
        """
        创建维修人员，处理密码加密
        
        参数：
            validated_data: 验证后的数据字典
            
        返回值：
            RepairStaff: 新创建的维修人员实例
        """
        # 移除确认密码字段
        validated_data.pop('confirm_password')
        
        # 加密密码
        from django.contrib.auth.hashers import make_password
        validated_data['password'] = make_password(validated_data['password'])
        
        # 创建维修人员
        staff = RepairStaff.objects.create(**validated_data)
        return staff


class AdministratorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Administrator
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password_strength]},
            'phone': {'validators': [validate_phone]}
        }
    
    def update(self, instance, validated_data):
        if 'password' in validated_data and validated_data['password']:
            instance.password = make_password(validated_data['password'])
            validated_data.pop('password')
        return super().update(instance, validated_data)
