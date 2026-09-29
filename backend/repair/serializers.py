"""
报修管理模块 - 序列化器定义

该模块定义了报修管理相关的序列化器，用于：
- 将模型实例转换为JSON格式的响应数据
- 将请求数据反序列化为模型实例
- 数据验证和关联数据处理

序列化器结构：
    RepairOrderSerializer
        - 报修工单的序列化和反序列化
        - 包含设备类型名称、校区显示等计算字段
    
    TransferRecordSerializer
        - 转派记录的序列化
        - 包含原/目标维修人员姓名
    
    StaffOnlineStatusSerializer
        - 维修人员在线状态的序列化
    
    AttachmentSerializer
        - 附件的序列化
    
    EvaluationSerializer
        - 评价的序列化和反序列化
        - 支持工单关联和评分计算
    
    EvaluationAppealSerializer
        - 评价申诉的序列化

作者：范广宇
创建日期：2026年
"""

from rest_framework import serializers
from .models import (RepairOrder, Evaluation, EvaluationAppeal, TransferRecord, 
                     StaffOnlineStatus, Attachment)


class _RepairOrderFieldMixin:
    def get_equipment_type_name(self, obj):
        try:
            if obj.equipment_type and hasattr(obj.equipment_type, 'type_name'):
                return obj.equipment_type.type_name
        except Exception:
            pass
        et = obj.equipment_type
        if et is None:
            return ''
        if isinstance(et, str):
            return et if not et.isdigit() else ''
        return str(et) if not str(et).isdigit() else ''

    def get_spare_parts_info(self, obj):
        try:
            parts = obj.used_parts.all()
            return [
                {
                    'spare_part_name': getattr(p.spare_part, 'name', '未知备件') if p.spare_part else '未知',
                    'quantity': p.quantity,
                }
                for p in parts
            ]
        except Exception:
            return []

    def get_scene_photos(self, obj):
        try:
            import json as _json
            sp = obj.scene_photo
            if not sp:
                return []
            if isinstance(sp, str):
                if sp.startswith('data:') or sp.startswith('http') or sp.startswith('/media'):
                    return [sp]
                if sp.startswith('['):
                    try:
                        parsed = _json.loads(sp)
                        return [p for p in parsed if p]
                    except Exception:
                        pass
                if '/' in sp or sp.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    path = sp if sp.startswith('/') else '/media/' + sp
                    return [path]
                return [sp]
            return []
        except Exception:
            return []


class RepairOrderListSerializer(_RepairOrderFieldMixin, serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=True, default='')
    equipment_type_name = serializers.SerializerMethodField()
    spare_parts_info = serializers.SerializerMethodField()
    scene_photos = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = [
            'id',
            'repair_no',
            'equipment',
            'equipment_name',
            'equipment_type',
            'equipment_type_name',
            'equipment_sequence_number',
            'location',
            'building',
            'floor',
            'room',
            'location_detail',
            'status',
            'is_urgent',
            'is_transferred',
            'staff',
            'staff_name',
            'user_name',
            'user_phone',
            'fault_count',
            'actual_duration',
            'spare_parts_info',
            'scene_photos',
            'complete_time',
            'accept_time',
            'repair_start_time',
            'created_at',
            'updated_at',
        ]


class RepairOrderSerializer(_RepairOrderFieldMixin, serializers.ModelSerializer):
    """
    报修工单序列化器
    
    用于报修工单的增删改查操作，包含多个计算字段和只读字段。
    
    计算字段：
        - equipment_type_name: 设备类型名称
        - campus_display: 校区显示名称
        - staff_phone: 维修人员联系电话
    
    只读字段：
        - repair_no: 报修编号（自动生成）
        - status: 工单状态（通过专门接口修改）
        - 用户和维修人员信息（自动从关联对象填充）
        - 时间节点字段（自动记录）
    
    使用场景：
        - 用户提交报修
        - 查询工单列表和详情
        - 更新工单信息
    """
    
    # 维修人员姓名（只读）
    staff_name = serializers.CharField(read_only=True, default='')
    
    # 设备类型名称（计算字段）
    equipment_type_name = serializers.SerializerMethodField()
    
    # 校区显示名称（计算字段）
    campus_display = serializers.SerializerMethodField()
    
    # 维修人员电话（计算字段）
    staff_phone = serializers.SerializerMethodField()
    
    # 使用备件信息（计算字段）
    spare_parts_info = serializers.SerializerMethodField()

    # 维修照片（计算字段，从Attachment表获取维修完成照片）
    repair_photos = serializers.SerializerMethodField()

    # 现场照片（计算字段，从scene_photo字段获取报修时上传的照片）
    scene_photos = serializers.SerializerMethodField()

    class Meta:
        model = RepairOrder
        fields = '__all__'
        # 只读字段列表，这些字段不能通过API直接修改
        read_only_fields = ['repair_no', 'status', 'reviewer', 'review_time',
                            'equipment_name', 'equipment_type',
                            'user_no', 'user_name', 'user_phone',
                            'staff_no', 'staff_name',
                            'accept_time', 'repair_start_time', 'repair_end_time',
                            'complete_time', 'actual_duration', 'is_deleted', 'deleted_at']

    def get_campus_display(self, obj):
        """
        获取校区显示名称
        
        直接返回location字段作为校区显示名称。
        
        参数：
            obj: RepairOrder实例
            
        返回值：
            str: 校区名称
        """
        return obj.location

    def get_staff_phone(self, obj):
        """
        获取维修人员联系电话
        
        从维修人员对象中获取联系电话。
        
        参数：
            obj: RepairOrder实例
            
        返回值：
            str: 维修人员电话，不存在则返回空字符串
        """
        if obj.staff_id:
            try:
                from users.models import RepairStaff
                staff = RepairStaff.objects.get(id=obj.staff_id)
                return getattr(staff, 'phone', '') or ''
            except Exception:
                pass
        return ''

    def get_repair_photos(self, obj):
        try:
            photos = []
            attachments = obj.attachments.filter(file_type='image')
            for a in attachments:
                if a.file_path:
                    path = a.file_path
                    if not path.startswith('http') and not path.startswith('data:') and not path.startswith('/media'):
                        path = '/media/' + path if not path.startswith('/') else path
                    photos.append(path)
            return photos
        except Exception:
            return []


class TransferRecordSerializer(serializers.ModelSerializer):
    """
    转派记录序列化器
    
    用于转派记录的查询操作，包含关联对象的名称字段。
    
    计算字段：
        - from_staff_name: 原维修人员姓名
        - to_staff_name: 目标维修人员姓名
        - order_no: 工单编号
    """
    
    # 原维修人员姓名
    from_staff_name = serializers.ReadOnlyField(source='from_staff.real_name')

    to_staff_name = serializers.ReadOnlyField(source='to_staff.real_name')
    
    # 工单编号
    order_no = serializers.ReadOnlyField(source='order.repair_no')
    
    class Meta:
        model = TransferRecord
        fields = '__all__'


class StaffOnlineStatusSerializer(serializers.ModelSerializer):
    """
    维修人员在线状态序列化器
    
    用于在线状态的查询和更新操作。
    
    计算字段：
        - staff_name: 维修人员姓名
        - staff_no: 维修人员账号
    """
    
    # 维修人员姓名
    staff_name = serializers.ReadOnlyField(source='staff.real_name')
    
    # 维修人员账号
    staff_no = serializers.ReadOnlyField(source='staff.staff_no')
    
    class Meta:
        model = StaffOnlineStatus
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    """
    附件序列化器
    
    用于附件的上传和查询操作。
    
    计算字段：
        - uploader_name: 上传者姓名
    
    只读字段：
        - uploader: 上传者（自动从请求用户获取）
    """
    
    # 上传者姓名
    uploader_name = serializers.ReadOnlyField(source='uploader.real_name')
    
    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['uploader']


class EvaluationSerializer(serializers.ModelSerializer):
    repair_no = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    staff_name = serializers.SerializerMethodField()
    order_id = serializers.IntegerField(read_only=True)
    equipment_name = serializers.SerializerMethodField(read_only=True)
    complete_time = serializers.SerializerMethodField(read_only=True)
    appeal_status = serializers.SerializerMethodField()
    
    repair_order = serializers.PrimaryKeyRelatedField(
        queryset=RepairOrder.objects.all(),
        source='order',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Evaluation
        exclude = ['order']
        read_only_fields = ['user', 'rating', 'is_deleted']

    def get_repair_no(self, obj):
        if obj.order:
            return obj.order.repair_no
        return ''

    def get_user_name(self, obj):
        if obj.user_name:
            return obj.user_name
        if obj.user:
            return getattr(obj.user, 'real_name', '') or str(obj.user.username)
        if obj.order and obj.order.user:
            return getattr(obj.order.user, 'real_name', '') or str(obj.order.user.username)
        if obj.order and obj.order.user_name:
            return obj.order.user_name
        return ''

    def get_staff_name(self, obj):
        if obj.staff_name:
            return obj.staff_name
        if obj.staff:
            return obj.staff.real_name
        if obj.order and obj.order.staff_name:
            return obj.order.staff_name
        return ''

    def get_equipment_name(self, obj):
        if obj.order:
            return getattr(obj.order, 'equipment_name', '') or ''
        return ''

    def get_complete_time(self, obj):
        if obj.order:
            return getattr(obj.order, 'complete_time', None) or getattr(obj.order, 'repair_end_time', None)
        return None

    def get_appeal_status(self, obj):
        appeal = EvaluationAppeal.objects.filter(evaluation=obj).first()
        if appeal:
            return appeal.status
        return ''


class EvaluationAppealSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    evaluation_detail = serializers.SerializerMethodField()
    repair_no = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationAppeal
        fields = '__all__'
    
    def get_staff_name(self, obj):
        if obj.staff_name:
            return obj.staff_name
        if obj.staff:
            return obj.staff.real_name
        return ''
    
    def get_evaluation_detail(self, obj):
        ev = obj.evaluation
        if ev:
            return {
                'rating': ev.rating,
                'content': ev.content or '',
                'quality_rating': ev.quality_rating,
                'speed_rating': ev.speed_rating,
                'attitude_rating': ev.attitude_rating
            }
        return None
    
    def get_repair_no(self, obj):
        if obj.evaluation and obj.evaluation.order:
            return obj.evaluation.order.repair_no
        return ''
