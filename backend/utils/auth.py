import jwt
import datetime
from functools import wraps
from flask import request, g, current_app
from .errors import error_response

def generate_token(user_id):
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        hours=current_app.config['JWT_EXPIRATION_HOURS']
    )
    payload = {'user_id': user_id, 'exp': exp}
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256']
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return error_response('未登录或Token已过期', 401, 'UNAUTHORIZED')
        token = auth_header[7:]
        user_id = verify_token(token)
        if user_id is None:
            return error_response('Token无效或已过期', 401, 'INVALID_TOKEN')
        g.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated

def get_current_user_id():
    return getattr(g, 'current_user_id', None)

def get_current_employee_id():
    uid = get_current_user_id()
    if not uid:
        return None
    from models.user import User
    user = User.query.get(uid)
    return user.employee_id if user else None

def require_permission(permission_code):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not has_permission(get_current_user_id(), permission_code):
                return error_response('无操作权限', 403, 'FORBIDDEN')
            return f(*args, **kwargs)
        return decorated
    return decorator

def has_permission(user_id, permission_code):
    from models import db
    from models.system import UserRole, RolePermission, Permission
    return db.session.query(UserRole).join(
        RolePermission, UserRole.role_id == RolePermission.role_id
    ).join(
        Permission, RolePermission.permission_id == Permission.permission_id
    ).filter(
        UserRole.user_id == user_id,
        Permission.permission_code == permission_code
    ).first() is not None
