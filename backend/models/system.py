from models import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Permission(db.Model):
    __tablename__ = 'permissions'
    permission_id = db.Column(db.Integer, primary_key=True)
    permission_code = db.Column(db.String(100), unique=True, nullable=False)
    permission_name = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='user_roles')
    role = db.relationship('Role', backref='user_roles')


class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role', backref='role_permissions')
    permission = db.relationship('Permission', backref='role_permissions')


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    log_type = db.Column(db.String(20), nullable=False)
    module = db.Column(db.String(50))
    action = db.Column(db.String(100))
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    log_time = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='system_logs')


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    log_id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    module = db.Column(db.String(50), nullable=False)
    operation = db.Column(db.String(30), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    target_name = db.Column(db.String(200))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    operator = db.relationship('Employee', backref='operation_logs')


class BackupRecord(db.Model):
    __tablename__ = 'backup_records'
    backup_id = db.Column(db.Integer, primary_key=True)
    backup_type = db.Column(db.String(20), nullable=False)
    backup_path = db.Column(db.String(255), nullable=False)
    backup_size = db.Column(db.BigInteger)
    status = db.Column(db.String(20), default='in_progress')
    executed_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    backup_time = db.Column(db.DateTime, default=datetime.utcnow)
    restore_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    executor = db.relationship('User', backref='backup_records')


class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    config_id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.String(20), default='system')
    description = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    updater = db.relationship('User', backref='system_configs')
