import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from importlib import import_module
from config import Config
from models import db
from utils.errors import success_response, error_response


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    db.init_app(app)

    from routes import register_blueprints
    register_blueprints(app)

    # 生产环境：提供前端静态文件
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.isdir(static_dir):
        @app.route('/')
        def serve_index():
            return send_from_directory(static_dir, 'index.html')

        @app.route('/favicon.ico')
        def serve_favicon():
            p = os.path.join(static_dir, 'favicon.ico')
            return send_from_directory(static_dir, 'favicon.ico') if os.path.exists(p) else ('', 204)

        @app.route('/<path:path>')
        def serve_frontend(path):
            if path.startswith('api'):
                return error_response('Not found', 404)
            file_path = os.path.join(static_dir, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(static_dir, path)
            return send_from_directory(static_dir, 'index.html')

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(405)
    @app.errorhandler(500)
    def json_error(e):
        from utils.errors import error_response
        return error_response(str(e) or '服务器内部错误', e.code if hasattr(e, 'code') else 500)

    with app.app_context():
        for module_name in [
            'models.user', 'models.product', 'models.supplier', 'models.purchase',
            'models.warehouse', 'models.sales', 'models.member', 'models.employee',
            'models.finance', 'models.system'
        ]:
            import_module(module_name)

        db.create_all()
        seed_permissions()
        seed_admin_user()

    @app.get('/api/health')
    def health_check():
        return success_response({'status': 'ok'})

    return app


def seed_permissions():
    from models.system import Permission
    perms = [
        # CRUD 权限（侧边栏需要）
        ('product:crud', '商品管理', 'product', '管理商品、分类与促销'),
        ('supplier:crud', '供应商管理', 'supplier', '管理供应商、合同与评价'),
        ('purchase:crud', '采购管理', 'purchase', '管理采购订单与入库'),
        ('warehouse:crud', '仓库管理', 'warehouse', '管理仓库配置与库存调整'),
        ('sales:crud', '销售管理', 'sales', '管理销售订单、退货与收银'),
        ('member:crud', '会员管理', 'member', '管理会员、等级与积分'),
        ('employee:crud', '员工管理', 'employee', '管理员工、排班与薪资'),
        ('finance:crud', '财务管理', 'finance', '管理账户、凭证与预算'),
        ('sys:manage', '系统管理', 'system', '管理用户、角色与权限'),
        # 审批权限
        ('purchase.approve', '采购审批', 'purchase', '审批采购订单'),
        ('sales.return.approve', '退货审批', 'sales', '审批销售退货单'),
        ('finance.journal.post', '凭证过账', 'finance', '会计分录过账'),
        ('finance.budget.approve', '预算审批', 'finance', '审批预算计划'),
        ('employee.payroll.approve', '工资审批', 'employee', '审批工资发放'),
        ('system.user.manage', '用户管理', 'system', '锁定/解锁用户'),
    ]
    for code, name, module, desc in perms:
        if not Permission.query.filter_by(permission_code=code).first():
            db.session.add(Permission(permission_code=code, permission_name=name, module=module, description=desc))
    db.session.commit()


def seed_admin_user():
    from models.user import User
    from models.system import Role, UserRole, Permission, RolePermission
    from werkzeug.security import generate_password_hash

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password_hash=generate_password_hash('admin123'), status='active')
        db.session.add(admin)
        db.session.flush()

    role = Role.query.filter_by(role_name='系统管理员').first()
    if not role:
        role = Role(role_name='系统管理员', description='全部权限')
        db.session.add(role)
        db.session.flush()

    if not UserRole.query.filter_by(user_id=admin.user_id, role_id=role.role_id).first():
        db.session.add(UserRole(user_id=admin.user_id, role_id=role.role_id))

    perms = Permission.query.all()
    for p in perms:
        if not RolePermission.query.filter_by(role_id=role.role_id, permission_id=p.permission_id).first():
            db.session.add(RolePermission(role_id=role.role_id, permission_id=p.permission_id))

    db.session.commit()


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
