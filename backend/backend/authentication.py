"""
自定义认证模块

提供基于 Token 的独立鉴权机制，解决三端（用户/维修/管理）Session 覆盖问题。

核心类：
    TokenAuthentication - DRF 认证类，从 Authorization 头读取 Token
    StaffUserWrapper - 维修人员身份包装器，兼容 request.user 接口
    AdminUserWrapper - 管理员身份包装器，兼容 request.user 接口

辅助函数：
    get_request_identity - 统一身份解析，返回 (user_type, user_id, identity_obj)
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import AuthToken, User, RepairStaff, Administrator

_token_cache = {}
_token_cache_max = 200


def _add_to_cache(token_key, user_type, user_id, identity, token_obj):
    if len(_token_cache) >= _token_cache_max:
        _token_cache.pop(next(iter(_token_cache)))
    _token_cache[token_key] = (user_type, user_id, identity, token_obj)


class StaffUserWrapper:
    """维修人员身份包装器，使 request.user.is_authenticated 等接口兼容 DRF"""

    is_authenticated = True
    is_staff = False
    is_superuser = False

    def __init__(self, staff):
        self._staff = staff
        self.id = staff.id
        self.pk = staff.id
        self.username = staff.staff_no

    @property
    def staff_id(self):
        return self._staff.id

    @property
    def real_name(self):
        return self._staff.real_name


class AdminUserWrapper:
    """管理员身份包装器，使 request.user.is_authenticated 等接口兼容 DRF"""

    is_authenticated = True
    is_staff = True
    is_superuser = True

    def __init__(self, admin):
        self._admin = admin
        self.id = admin.id
        self.pk = admin.id
        self.username = admin.admin_no

    @property
    def admin_id(self):
        return self._admin.id

    @property
    def real_name(self):
        return self._admin.real_name


class TokenAuthentication(BaseAuthentication):
    """
    基于 DB Token 的认证类

    从请求头 Authorization: Token <key> 读取 Token，
    查询 AuthToken 表获取 user_type + user_id，
    解析出对应的身份对象并设置到 request 上。

    额外设置到 request 的属性：
        request.auth_user_type - 'user' / 'staff' / 'admin'
        request.auth_identity - 原始身份对象（User / RepairStaff / Administrator 实例）
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Token '):
            return None

        token_key = auth_header[6:].strip()
        if not token_key:
            return None

        cached = _token_cache.get(token_key)
        if cached:
            user_type, user_id, identity, token_obj = cached
            request.auth_user_type = user_type
            request.auth_identity = identity
            if user_type == 'user':
                return (identity, token_obj)
            elif user_type == 'staff':
                return (StaffUserWrapper(identity), token_obj)
            elif user_type == 'admin':
                return (AdminUserWrapper(identity), token_obj)

        try:
            token = AuthToken.objects.get(key=token_key)
        except AuthToken.DoesNotExist:
            raise AuthenticationFailed('无效的Token')

        if token.user_type == 'user':
            try:
                user = User.objects.get(id=token.user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('用户不存在')
            request.auth_user_type = 'user'
            request.auth_identity = user
            _add_to_cache(token_key, 'user', user.id, user, token)
            return (user, token)

        elif token.user_type == 'staff':
            try:
                staff = RepairStaff.objects.get(id=token.user_id)
            except RepairStaff.DoesNotExist:
                raise AuthenticationFailed('维修员不存在')
            wrapper = StaffUserWrapper(staff)
            request.auth_user_type = 'staff'
            request.auth_identity = staff
            _add_to_cache(token_key, 'staff', staff.id, staff, token)
            return (wrapper, token)

        elif token.user_type == 'admin':
            try:
                admin = Administrator.objects.get(id=token.user_id)
            except Administrator.DoesNotExist:
                raise AuthenticationFailed('管理员不存在')
            wrapper = AdminUserWrapper(admin)
            request.auth_user_type = 'admin'
            request.auth_identity = admin
            _add_to_cache(token_key, 'admin', admin.id, admin, token)
            return (wrapper, token)

        raise AuthenticationFailed('未知的用户类型')

    def authenticate_header(self, request):
        return 'Token'


def get_request_identity(request):
    """
    统一身份解析函数

    从 Token 认证结果中获取当前请求的身份信息。
    所有后端视图应使用此函数获取身份，不再读取 session 或 query_params。

    参数：
        request: DRF Request 对象

    返回值：
        tuple: (user_type, user_id, identity_obj)
            user_type: 'user' / 'staff' / 'admin' / None
            user_id: 对应模型的 PK / None
            identity_obj: User / RepairStaff / Administrator 实例 / None
    """
    # 优先从 Token 认证结果获取
    user_type = getattr(request, 'auth_user_type', None)
    if user_type:
        identity = getattr(request, 'auth_identity', None)
        if identity:
            return (user_type, identity.id, identity)

    # 兼容：Django 认证用户（Token 认证中 user_type 已设置，此处为额外保障）
    if hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        # 判断是否为 wrapper
        if isinstance(user, StaffUserWrapper):
            return ('staff', user.staff_id, request.auth_identity)
        elif isinstance(user, AdminUserWrapper):
            return ('admin', user.admin_id, request.auth_identity)
        else:
            return ('user', user.id, user)

    return (None, None, None)
