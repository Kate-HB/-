from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import generate_token, require_auth
from utils.operation_log import log_operation
from datetime import datetime, timezone

bp = Blueprint('auth', __name__)


@bp.route('/api/login', methods=['POST'])
def login():
    data, err = get_json()
    if err: return err
    username = data.get('username', '')
    password = data.get('password', '')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error_response('用户名或密码错误', 401)
    if user.status != 'active':
        return error_response('账号已被禁用', 403)
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    log_operation('system', 'login', 'User', user.user_id, user.username)
    token = generate_token(user.user_id)

    from models.system import UserRole, RolePermission, Permission
    user_roles = UserRole.query.filter_by(user_id=user.user_id).all()
    role_ids = [ur.role_id for ur in user_roles]
    perms = set()
    if role_ids:
        rows = RolePermission.query.filter(RolePermission.role_id.in_(role_ids)).all()
        perm_ids = [rp.permission_id for rp in rows]
        if perm_ids:
            perms = {p.permission_code for p in Permission.query.filter(Permission.permission_id.in_(perm_ids)).all()}

    return jsonify(success_response({
        'token': token,
        'user': {
            'user_id': user.user_id,
            'username': user.username,
            'employee_id': user.employee_id,
            'roles': [{'role_id': ur.role_id, 'role_name': ur.role.role_name} for ur in user_roles],
            'permissions': list(perms)
        }
    }, '登录成功'))


@bp.route('/api/register', methods=['POST'])
@require_auth
def register():
    data, err = get_json()
    if err: return err
    username = data.get('username', '')
    password = data.get('password', '')
    if not username or not password:
        return error_response('用户名和密码不能为空')
    if User.query.filter_by(username=username).first():
        return error_response('用户名已存在')
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_operation('system', 'register', 'User', user.user_id, data.get('username', ''))
    token = generate_token(user.user_id)
    return jsonify(success_response({
        'token': token,
        'user': {'user_id': user.user_id, 'username': user.username}
    }, '注册成功'))


@bp.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    return jsonify(success_response(message='已退出'))
