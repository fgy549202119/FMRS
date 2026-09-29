"""
用户管理模块 - 视图函数定义

该模块提供了用户管理相关的API视图，包括：
- 普通用户的注册、登录、登出、个人信息管理
- 维修人员的登录和账号管理
- 管理员的登录和账号管理

视图集结构：
    UserViewSet
        - 用户CRUD操作
        - 登录/登出功能
        - 个人信息查询和修改
        - 密码修改
        - 批量删除
    
    RepairStaffViewSet
        - 维修人员CRUD操作
        - 维修人员登录
    
    AdministratorViewSet
        - 管理员CRUD操作
        - 管理员登录

认证机制：
    - User使用Django内置的认证系统（session认证）
    - RepairStaff和Administrator使用独立的session认证
    - 所有视图都跳过CSRF验证，适配前后端分离架构

作者：范广宇
创建日期：2026年
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, RepairStaff, Administrator, AuthToken, MessageBoard
from .serializers import (
    UserSerializer, UserRegisterSerializer,
    RepairStaffSerializer, RepairStaffRegisterSerializer,
    AdministratorSerializer, MessageBoardSerializer
)
from backend.authentication import get_request_identity


@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    """
    普通用户视图集
    
    该视图集提供普通用户的完整CRUD操作，以及登录、登出、
    个人信息管理等自定义操作。
    
    继承自ModelViewSet，自动提供以下操作：
        - list: GET /api/user/users/ - 获取用户列表
        - create: POST /api/user/users/ - 创建用户（注册）
        - retrieve: GET /api/user/users/{id}/ - 获取单个用户详情
        - update: PUT /api/user/users/{id}/ - 更新用户信息
        - partial_update: PATCH /api/user/users/{id}/ - 部分更新用户信息
        - destroy: DELETE /api/user/users/{id}/ - 删除用户
    
    自定义操作：
        - login: POST /api/user/users/login/ - 用户登录
        - logout: POST /api/user/users/logout/ - 用户登出
        - profile: GET /api/user/users/profile/ - 获取当前登录用户信息
        - change_password: POST /api/user/users/change_password/ - 修改密码
        - batch_delete: POST /api/user/users/batch_delete/ - 批量删除用户
    
    权限设置：
        - 所有操作允许任意用户访问（AllowAny）
        - 具体权限控制在前端路由中实现
    """
    
    # 查询集：获取所有用户
    queryset = User.objects.all()
    
    # 默认序列化器
    serializer_class = UserSerializer
    
    # 权限类：允许所有用户访问
    permission_classes = [AllowAny]
    
    # 过滤后端
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    
    # 可搜索字段
    search_fields = ['username', 'real_name']
    
    # 可过滤字段
    filterset_fields = ['user_type']
    
    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        
        创建用户（注册）时使用UserRegisterSerializer，
        包含确认密码验证逻辑。
        其他操作使用UserSerializer。
        
        返回值：
            Serializer类: 根据操作类型返回对应的序列化器
        """
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                'code': 400,
                'message': '用户名或密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        if user.user_type not in ('student', 'teacher'):
            return Response({
                'code': 400,
                'message': '该账号无法通过用户端登录'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(password, user.password):
            return Response({
                'code': 400,
                'message': '用户名或密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)

        token = AuthToken.generate('user', user.id)
        serializer = UserSerializer(user)
        return Response({
            'code': 200,
            'message': '登录成功',
            'data': serializer.data,
            'token': token.key
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        用户登出接口
        
        清除当前用户的会话信息。
        
        请求方式：
            POST /api/user/users/logout/
        
        返回格式：
            {
                'code': 200,
                'message': '退出成功'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含登出结果的响应对象
        """
        # 删除当前用户的 Token
        if hasattr(request, 'auth') and request.auth:
            request.auth.delete()
        return Response({
            'code': 200,
            'message': '退出成功'
        })
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        获取当前登录用户信息
        
        返回当前已登录用户的详细信息。
        
        请求方式：
            GET /api/user/users/profile/
        
        返回格式：
            已登录：{
                'code': 200,
                'data': {用户信息}
            }
            未登录：{
                'code': 401,
                'message': '未登录'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含用户信息的响应对象
        """
        if request.user.is_authenticated:
            # 从数据库重新查询用户信息，避免token缓存导致返回旧数据
            try:
                user = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                return Response({'code': 401, 'message': '用户不存在'}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = UserSerializer(user)
            return Response({
                'code': 200,
                'data': serializer.data
            })
        
        # 用户未登录
        return Response({
            'code': 401,
            'message': '未登录'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改密码接口
        
        验证原密码后更新用户密码。
        
        请求方式：
            POST /api/user/users/change_password/
        
        请求参数：
            - old_password: 原密码
            - new_password: 新密码
        
        返回格式：
            成功：{
                'code': 200,
                'message': '密码修改成功'
            }
            失败：{
                'code': 400/401,
                'message': '错误信息'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含修改结果的响应对象
        """
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return Response({
                'code': 401,
                'message': '未登录'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 获取请求参数
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        # 验证原密码是否正确
        if not request.user.check_password(old_password):
            return Response({
                'code': 400,
                'message': '原密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 设置新密码（自动加密）
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'code': 200,
            'message': '密码修改成功'
        })
    
    @action(detail=False, methods=['post'])
    def delete_account(self, request):
        """
        账号注销接口
        
        验证密码后注销用户账号。
        
        请求方式：
            POST /api/user/users/delete_account/
        
        请求参数：
            - password: 用户密码
        
        返回格式：
            成功：{
                'code': 200,
                'message': '账号注销成功'
            }
            失败：{
                'code': 400/401,
                'message': '错误信息'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含注销结果的响应对象
        """
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return Response({
                'code': 401,
                'message': '未登录'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 获取请求参数
        password = request.data.get('password')
        
        # 验证密码是否正确
        if not request.user.check_password(password):
            return Response({
                'code': 400,
                'message': '密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = request.user.id
        request.user.delete()
        AuthToken.objects.filter(user_type='user', user_id=user_id).delete()

        return Response({
            'code': 200,
            'message': '账号注销成功'
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def batch_delete(self, request):
        """
        批量删除用户接口
        
        根据提供的用户ID列表批量删除用户。
        管理员账号不允许被删除。
        
        请求方式：
            POST /api/user/users/batch_delete/
        
        请求参数：
            - ids: 用户ID列表 [1, 2, 3, ...]
        
        返回格式：
            成功：{
                'code': 200,
                'message': '成功删除 N 个用户'
            }
            失败：{
                'code': 400,
                'message': '请选择要删除的用户'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含删除结果的响应对象
        """
        ids = request.data.get('ids', [])
        
        if not ids:
            return Response({
                'code': 400,
                'message': '请选择要删除的用户'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        admin_count = User.objects.filter(id__in=ids, user_type='admin').count()
        if admin_count > 0:
            return Response({
                'code': 400,
                'message': '管理员账号不允许删除'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = User.objects.filter(id__in=ids).delete()
        
        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 个用户'
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user_type == 'admin':
            return Response({
                'code': 400,
                'message': '管理员账号不允许删除'
            }, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({
            'code': 200,
            'message': '删除成功'
        })
    
    def create(self, request, *args, **kwargs):
        """
        创建用户（注册）
        
        重写create方法，使用UserRegisterSerializer进行数据验证和用户创建。
        
        参数：
            request: DRF Request对象
            *args, **kwargs: 其他参数
            
        返回值：
            Response: 包含创建结果的响应对象
        """
        try:
            # 调用父类的create方法，会自动使用get_serializer_class返回的序列化器
            response = super().create(request, *args, **kwargs)
            
            # 返回自定义格式的响应
            return Response({
                'code': 200,
                'message': '注册成功',
                'data': response.data
            })
        except ValidationError as e:
            error_messages = []
            for field, errors in e.detail.items():
                for error in errors:
                    # 将username字段的唯一性错误转为友好提示
                    if field == 'username' and ('already exist' in str(error).lower() or '已存在' in str(error)):
                        error_messages.append('该账号已存在，请更换账号后重试')
                    else:
                        error_messages.append(f'{field}: {error}')
            error_message = '; '.join(error_messages)
            return Response({
                'code': 400,
                'message': f'注册失败: {error_message}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 400,
                'message': f'注册失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class RepairStaffViewSet(viewsets.ModelViewSet):
    """
    维修人员视图集
    
    该视图集提供维修人员的完整CRUD操作，以及登录功能。
    维修人员使用独立的认证系统，不依赖Django的User模型。
    
    继承自ModelViewSet，自动提供以下操作：
        - list: GET /api/user/staff/ - 获取维修人员列表
        - create: POST /api/user/staff/ - 创建维修人员
        - retrieve: GET /api/user/staff/{id}/ - 获取单个维修人员详情
        - update: PUT /api/user/staff/{id}/ - 更新维修人员信息
        - partial_update: PATCH /api/user/staff/{id}/ - 部分更新
        - destroy: DELETE /api/user/staff/{id}/ - 删除维修人员
    
    自定义操作：
        - login: POST /api/user/staff/login/ - 维修人员登录
    
    认证机制：
        - 使用session存储登录状态
        - session中存储staff_id和role标识
    """
    
    # 查询集：获取所有维修人员
    queryset = RepairStaff.objects.all()
    
    serializer_class = RepairStaffSerializer
    
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['status', 'is_active']
    search_fields = ['staff_no', 'real_name', 'phone']
    
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """
        返回序列化器类
        
        当前所有操作都使用RepairStaffSerializer。
        
        返回值：
            Serializer类: RepairStaffSerializer
        """
        return RepairStaffSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        维修人员登录接口
        
        验证维修人员的账号和密码，成功后在session中存储登录信息。
        
        请求方式：
            POST /api/user/staff/login/
        
        请求参数：
            - staff_no: 维修人员账号
            - password: 密码
        
        返回格式：
            成功：{
                'code': 200,
                'message': '登录成功',
                'data': {维修人员信息}
            }
            失败：{
                'code': 400,
                'message': '账号或密码错误'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含登录结果的响应对象
        """
        # 获取请求参数
        staff_no = request.data.get('staff_no')
        password = request.data.get('password')
        
        try:
            # 查询维修人员
            staff = RepairStaff.objects.get(staff_no=staff_no)
            
            # 验证密码（使用Django的密码检查函数）
            if check_password(password, staff.password):
                # 验证成功，生成 Token（替代 Session）
                token = AuthToken.generate('staff', staff.id)
                serializer = RepairStaffSerializer(staff)
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': serializer.data,
                    'token': token.key
                })
        except RepairStaff.DoesNotExist:
            pass
        
        # 验证失败
        return Response({
            'code': 400,
            'message': '账号或密码错误'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        维修人员登出接口

        删除当前维修人员的 Token，更新在线状态。
        """
        from backend.authentication import get_request_identity
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'staff' and user_id:
            AuthToken.objects.filter(user_type='staff', user_id=user_id).delete()
            # 更新在线状态
            from repair.models import StaffOnlineStatus
            StaffOnlineStatus.objects.filter(staff_id=user_id).update(is_online=False)
            if identity:
                identity.is_online = False
                identity.status = 'offline'
                identity.save()
        return Response({'code': 200, 'message': '退出成功'})


@method_decorator(csrf_exempt, name='dispatch')
class AdministratorViewSet(viewsets.ModelViewSet):
    """
    管理员视图集
    
    该视图集提供管理员的完整CRUD操作，以及登录功能。
    管理员使用独立的认证系统，不依赖Django的User模型。
    
    继承自ModelViewSet，自动提供以下操作：
        - list: GET /api/user/admin/ - 获取管理员列表
        - create: POST /api/user/admin/ - 创建管理员
        - retrieve: GET /api/user/admin/{id}/ - 获取单个管理员详情
        - update: PUT /api/user/admin/{id}/ - 更新管理员信息
        - partial_update: PATCH /api/user/admin/{id}/ - 部分更新
        - destroy: DELETE /api/user/admin/{id}/ - 删除管理员
    
    自定义操作：
        - login: POST /api/user/admin/login/ - 管理员登录
    
    认证机制：
        - 使用session存储登录状态
        - session中存储admin_id和role标识
    """
    
    # 查询集：获取所有管理员
    queryset = Administrator.objects.all()
    
    # 序列化器
    serializer_class = AdministratorSerializer
    
    # 权限类：允许所有用户访问
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        管理员登录接口
        
        验证管理员的账号和密码，成功后在session中存储登录信息。
        
        请求方式：
            POST /api/user/admin/login/
        
        请求参数：
            - admin_no: 管理员账号
            - password: 密码
        
        返回格式：
            成功：{
                'code': 200,
                'message': '登录成功',
                'data': {管理员信息}
            }
            失败：{
                'code': 400,
                'message': '账号或密码错误'
            }
        
        参数：
            request: DRF Request对象
            
        返回值：
            Response: 包含登录结果的响应对象
        """
        # 获取请求参数
        admin_no = request.data.get('admin_no')
        password = request.data.get('password')
        
        try:
            # 查询管理员
            admin = Administrator.objects.get(admin_no=admin_no)
            
            # 验证密码
            if check_password(password, admin.password):
                # 验证成功，生成 Token（替代 Session）
                token = AuthToken.generate('admin', admin.id)
                serializer = AdministratorSerializer(admin)
                return Response({
                    'code': 200,
                    'message': '登录成功',
                    'data': serializer.data,
                    'token': token.key
                })
        except Administrator.DoesNotExist:
            pass

        # 验证失败
        return Response({
            'code': 400,
            'message': '账号或密码错误'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        管理员登出接口

        删除当前管理员的 Token。
        """
        from backend.authentication import get_request_identity
        user_type, user_id, identity = get_request_identity(request)
        if user_type == 'admin' and user_id:
            AuthToken.objects.filter(user_type='admin', user_id=user_id).delete()
        return Response({'code': 200, 'message': '退出成功'})


@method_decorator(csrf_exempt, name='dispatch')
class MessageBoardViewSet(viewsets.ModelViewSet):
    queryset = MessageBoard.objects.filter(is_deleted=False).select_related('user')
    serializer_class = MessageBoardSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_type, user_id, identity = get_request_identity(self.request)
        if user_type == 'admin':
            return MessageBoard.objects.filter(is_deleted=False).select_related('user')
        if user_type == 'user' and user_id:
            return MessageBoard.objects.filter(user_id=user_id, is_deleted=False).select_related('user')
        return MessageBoard.objects.filter(is_deleted=False).select_related('user')

    def perform_create(self, serializer):
        user_type, user_id, identity = get_request_identity(self.request)
        if user_type == 'user' and identity:
            serializer.save(user=identity)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted', 'updated_at'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'code': 200,
            'message': '留言成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })
