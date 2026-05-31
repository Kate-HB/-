from flask import Blueprint, request, jsonify
from models import db
from models.user import User
from models.system import Role, Permission, UserRole, RolePermission, SystemLog, OperationLog, BackupRecord, SystemConfig
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id, get_current_user_id
from utils.operation_log import log_operation
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload

bp = Blueprint('system', __name__)


# ==================== Users ====================

@bp.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')

    q = User.query.options(joinedload(User.user_roles).joinedload(UserRole.role))
    if search:
        q = q.filter(User.username.contains(search))

    total = q.count()
    rows = q.order_by(User.user_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'user_id': r.user_id,
        'username': r.username,
        'employee_id': r.employee_id,
        'status': r.status,
        'last_login': r.last_login.isoformat() if r.last_login else None,
        'roles': [{'role_id': ur.role_id, 'role_name': ur.role.role_name if ur.role else ''} for ur in r.user_roles],
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/users', methods=['POST'])
@require_auth
@require_permission('system.user.manage')
def add_user():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'username')
    if missing: return error_response(f'缺少必填字段: {missing}')
    if User.query.filter_by(username=data['username']).first():
        return error_response('用户名已存在')
    user = User(username=data['username'])
    user.set_password(data.get('password', '123456'))
    user.employee_id = data.get('employee_id')
    user.status = data.get('status', 'active')
    db.session.add(user)
    db.session.flush()

    for role_id in data.get('role_ids', []):
        ur = UserRole(user_id=user.user_id, role_id=role_id)
        db.session.add(ur)

    db.session.commit()
    log_operation('system', 'create', 'User', user.user_id, data.get('username', ''))
    return jsonify(success_response({'user_id': user.user_id}, '用户添加成功'))


@bp.route('/api/users/<int:id>', methods=['PUT'])
@require_auth
@require_permission('system.user.manage')
def update_user(id):
    user = User.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['username', 'employee_id', 'status']:
        if field in data:
            setattr(user, field, data[field])
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    if 'role_ids' in data:
        UserRole.query.filter_by(user_id=id).delete()
        for role_id in data['role_ids']:
            ur = UserRole(user_id=id, role_id=role_id)
            db.session.add(ur)
    db.session.commit()
    log_operation('system', 'update', 'User', id, data.get('username') or user.username)
    return jsonify(success_response(message='用户更新成功'))


@bp.route('/api/users/<int:id>/lock', methods=['PUT'])
@require_auth
@require_permission('system.user.manage')
def toggle_user_lock(id):
    user = User.query.get_or_404(id)
    user.status = 'active' if user.status == 'locked' else 'locked'
    db.session.commit()
    log_operation('system', 'update', 'User', id, user.username)
    return jsonify(success_response(message=f'用户已{user.status}'))


# ==================== Roles ====================

@bp.route('/api/roles', methods=['GET'])
@require_auth
def get_roles():
    rows = Role.query.options(joinedload(Role.role_permissions)).all()
    result = [{
        'role_id': r.role_id,
        'role_name': r.role_name,
        'description': r.description,
        'permission_ids': [rp.permission_id for rp in r.role_permissions]
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/roles', methods=['POST'])
@require_auth
@require_permission('sys:manage')
def add_role():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'role_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    role = Role(
        role_name=data['role_name'],
        description=data.get('description', '')
    )
    db.session.add(role)
    db.session.flush()

    for perm_id in data.get('permission_ids', []):
        rp = RolePermission(role_id=role.role_id, permission_id=perm_id)
        db.session.add(rp)

    db.session.commit()
    log_operation('system', 'create', 'Role', role.role_id, data.get('role_name', ''))
    return jsonify(success_response({'role_id': role.role_id}, '角色添加成功'))


@bp.route('/api/roles/<int:id>', methods=['PUT'])
@require_auth
@require_permission('sys:manage')
def update_role(id):
    role = Role.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['role_name', 'description']:
        if field in data:
            setattr(role, field, data[field])
    if 'permission_ids' in data:
        RolePermission.query.filter_by(role_id=id).delete()
        for perm_id in data['permission_ids']:
            rp = RolePermission(role_id=id, permission_id=perm_id)
            db.session.add(rp)
    db.session.commit()
    log_operation('system', 'update', 'Role', id, data.get('role_name') or role.role_name)
    return jsonify(success_response(message='角色更新成功'))


@bp.route('/api/roles/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('sys:manage')
def delete_role(id):
    role = Role.query.get_or_404(id)
    RolePermission.query.filter_by(role_id=id).delete()
    UserRole.query.filter_by(role_id=id).delete()
    db.session.delete(role)
    db.session.commit()
    log_operation('system', 'delete', 'Role', id, role.role_name)
    return jsonify(success_response(message='角色删除成功'))


# ==================== Permissions ====================

@bp.route('/api/permissions', methods=['GET'])
@require_auth
def get_permissions():
    rows = Permission.query.all()
    result = [{
        'permission_id': r.permission_id,
        'permission_code': r.permission_code,
        'permission_name': r.permission_name,
        'module': r.module,
        'description': r.description
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/permissions', methods=['POST'])
@require_auth
@require_permission('sys:manage')
def add_permission():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'permission_code', 'permission_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    perm = Permission(
        permission_code=data['permission_code'],
        permission_name=data['permission_name'],
        module=data.get('module', ''),
        description=data.get('description', '')
    )
    db.session.add(perm)
    db.session.commit()
    log_operation('system', 'create', 'Permission', perm.permission_id, data.get('permission_code', ''))
    return jsonify(success_response({'permission_id': perm.permission_id}, '权限添加成功'))


@bp.route('/api/permissions/<int:id>', methods=['PUT'])
@require_auth
@require_permission('sys:manage')
def update_permission(id):
    perm = Permission.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['permission_code', 'permission_name', 'module', 'description']:
        if field in data:
            setattr(perm, field, data[field])
    db.session.commit()
    log_operation('system', 'update', 'Permission', id, data.get('permission_code') or perm.permission_code)
    return jsonify(success_response(message='权限更新成功'))


@bp.route('/api/permissions/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('sys:manage')
def delete_permission(id):
    perm = Permission.query.get_or_404(id)
    RolePermission.query.filter_by(permission_id=id).delete()
    db.session.delete(perm)
    db.session.commit()
    log_operation('system', 'delete', 'Permission', id, perm.permission_code)
    return jsonify(success_response(message='权限删除成功'))


# ==================== Logs ====================

@bp.route('/api/logs', methods=['GET'])
@require_auth
def get_logs():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    log_type = request.args.get('log_type', '')

    q = SystemLog.query
    if log_type:
        q = q.filter(SystemLog.log_type == log_type)

    total = q.count()
    rows = q.order_by(SystemLog.log_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'log_id': r.log_id,
        'log_type': r.log_type,
        'module': r.module,
        'action': r.action,
        'description': r.description,
        'user_id': r.user_id,
        'username': r.user.username if r.user else '',
        'ip_address': r.ip_address,
        'log_time': r.log_time.isoformat() if r.log_time else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


# ==================== Operation Logs ====================

@bp.route('/api/operation-logs', methods=['GET'])
@require_auth
def get_operation_logs():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    module = request.args.get('module', '').strip()
    operation = request.args.get('operation', '').strip()
    operator_id = request.args.get('operator_id', type=int)
    search = request.args.get('search', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    q = OperationLog.query
    if module:
        q = q.filter(OperationLog.module == module)
    if operation:
        q = q.filter(OperationLog.operation == operation)
    if operator_id:
        q = q.filter(OperationLog.operator_id == operator_id)
    if search:
        pattern = f'%{search}%'
        q = q.filter(
            db.or_(
                OperationLog.target_name.contains(pattern),
                OperationLog.target_type.contains(pattern),
                OperationLog.module.contains(pattern)
            )
        )
    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            q = q.filter(OperationLog.created_at >= sd)
        except (ValueError, TypeError):
            pass
    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            q = q.filter(OperationLog.created_at <= ed.replace(hour=23, minute=59, second=59))
        except (ValueError, TypeError):
            pass

    total = q.count()
    rows = q.order_by(OperationLog.log_id.desc()) \
        .offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'log_id': r.log_id,
        'operator_id': r.operator_id,
        'operator_name': r.operator.employee_name if r.operator else '',
        'module': r.module,
        'operation': r.operation,
        'target_type': r.target_type,
        'target_id': r.target_id,
        'target_name': r.target_name,
        'details': r.details,
        'ip_address': r.ip_address,
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


# ==================== System Configs ====================

@bp.route('/api/system-configs', methods=['GET'])
@require_auth
def get_system_configs():
    rows = SystemConfig.query.all()
    result = [{
        'config_id': r.config_id,
        'config_key': r.config_key,
        'config_value': r.config_value,
        'config_type': r.config_type,
        'description': r.description,
        'updated_at': r.updated_at.isoformat() if r.updated_at else None
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/system-configs', methods=['POST'])
@require_auth
@require_permission('sys:manage')
def add_system_config():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'config_key', 'config_value')
    if missing: return error_response(f'缺少必填字段: {missing}')
    cfg = SystemConfig(
        config_key=data['config_key'],
        config_value=data['config_value'],
        config_type=data.get('config_type', 'system'),
        description=data.get('description', '')
    )
    db.session.add(cfg)
    db.session.commit()
    log_operation('system', 'create', 'SystemConfig', cfg.config_id, data.get('config_key', ''))
    return jsonify(success_response({'config_id': cfg.config_id}, '配置添加成功'))


@bp.route('/api/system-configs/<int:id>', methods=['PUT'])
@require_auth
@require_permission('sys:manage')
def update_system_config(id):
    cfg = SystemConfig.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['config_key', 'config_value', 'config_type', 'description']:
        if field in data:
            setattr(cfg, field, data[field])
    cfg.updated_by = get_current_employee_id()
    db.session.commit()
    log_operation('system', 'update', 'SystemConfig', id, data.get('config_key') or cfg.config_key)
    return jsonify(success_response(message='配置更新成功'))


# ==================== Backup Records ====================

@bp.route('/api/backup-records', methods=['GET'])
@require_auth
def get_backup_records():
    rows = BackupRecord.query.order_by(BackupRecord.backup_id.desc()).limit(50).all()
    result = [{
        'backup_id': r.backup_id,
        'backup_type': r.backup_type,
        'backup_path': r.backup_path,
        'backup_size': r.backup_size,
        'status': r.status,
        'backup_time': r.backup_time.isoformat() if r.backup_time else None,
        'restore_time': r.restore_time.isoformat() if r.restore_time else None
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/backup-records', methods=['POST'])
@require_auth
def add_backup_record():
    import shutil
    from pathlib import Path
    data, err = get_json()
    if err: return err

    backup_dir = Path(__file__).resolve().parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)

    backup_type = data.get('backup_type', 'full')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'backup_{backup_type}_{timestamp}.db'
    backup_path = backup_dir / backup_filename

    db_path = Path(__file__).resolve().parent.parent / 'supermarket.db'
    try:
        shutil.copy2(str(db_path), str(backup_path))
        backup_size = backup_path.stat().st_size
    except Exception as e:
        return error_response(f'备份失败: {str(e)}')

    br = BackupRecord(
        backup_type=backup_type,
        backup_path=str(backup_path),
        backup_size=backup_size,
        status='success',
        executed_by=get_current_employee_id()
    )
    db.session.add(br)
    db.session.commit()
    log_operation('system', 'create', 'BackupRecord', br.backup_id, backup_type)
    return jsonify(success_response({'backup_id': br.backup_id, 'backup_path': str(backup_path)}, '备份创建成功'))
