from flask import Flask
from flask_cors import CORS
from importlib import import_module
from config import Config
from models import db
from utils.errors import success_response


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    db.init_app(app)

    from routes import register_blueprints
    register_blueprints(app)

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

    @app.get('/api/health')
    def health_check():
        return success_response({'status': 'ok'})

    return app


def seed_permissions():
    from models.system import Permission
    perms = [
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


app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
