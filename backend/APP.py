import os
import random
from datetime import datetime, date, timedelta
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
        try:
            seed_permissions()
        except Exception as e:
            db.session.rollback()
            print(f'[seed] permissions error: {e}')
        try:
            seed_test_data()
        except Exception as e:
            db.session.rollback()
            print(f'[seed] test_data error: {e}')

    @app.get('/api/health')
    def health_check():
        return success_response({'status': 'ok'})

    @app.post('/api/admin/seed')
    def admin_seed():
        try:
            seed_permissions()
            seed_test_data()
            return success_response({'status': 'ok'}, '测试数据已生成')
        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

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


def seed_test_data():
    from models.employee import Position, Employee
    from models.user import User
    from models.system import Role, UserRole, Permission, RolePermission
    from werkzeug.security import generate_password_hash

    from models.product import Product as PD
    if PD.query.first():
        return

    print('[seed] Creating test data...')

    # ── Users & Roles ──
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password_hash=generate_password_hash('admin123'), status='active')
        db.session.add(admin)
        db.session.flush()
    zhangsan = User.query.filter_by(username='zhangsan').first()
    if not zhangsan:
        zhangsan = User(username='zhangsan', password_hash=generate_password_hash('123456'), status='active')
        db.session.add(zhangsan)
        db.session.flush()
    lisi = User.query.filter_by(username='lisi').first()
    if not lisi:
        lisi = User(username='lisi', password_hash=generate_password_hash('123456'), status='active')
        db.session.add(lisi)
        db.session.flush()

    role_admin = Role.query.filter_by(role_name='系统管理员').first()
    if not role_admin:
        role_admin = Role(role_name='系统管理员', description='全部权限')
        db.session.add(role_admin)
        db.session.flush()
    role_mgr = Role.query.filter_by(role_name='经理').first()
    if not role_mgr:
        role_mgr = Role(role_name='经理', description='管理权限')
        db.session.add(role_mgr)
        db.session.flush()
    role_staff = Role.query.filter_by(role_name='员工').first()
    if not role_staff:
        role_staff = Role(role_name='员工', description='基础权限')
        db.session.add(role_staff)
        db.session.flush()

    for uid, rid in [(admin.user_id, role_admin.role_id), (zhangsan.user_id, role_mgr.role_id), (lisi.user_id, role_staff.role_id)]:
        if not UserRole.query.filter_by(user_id=uid, role_id=rid).first():
            db.session.add(UserRole(user_id=uid, role_id=rid))

    # Assign all permissions to admin
    all_perms = Permission.query.all()
    for p in all_perms:
        if not RolePermission.query.filter_by(role_id=role_admin.role_id, permission_id=p.permission_id).first():
            db.session.add(RolePermission(role_id=role_admin.role_id, permission_id=p.permission_id))
    # Manager: crud + approve (no sys)
    mgr_codes = ['product:crud','supplier:crud','purchase:crud','warehouse:crud','sales:crud',
                 'member:crud','employee:crud','finance:crud',
                 'purchase.approve','sales.return.approve','finance.journal.post','finance.budget.approve','employee.payroll.approve']
    staff_codes = ['product:crud','sales:crud','member:crud','warehouse:crud','purchase:crud']
    for code in mgr_codes:
        p = Permission.query.filter_by(permission_code=code).first()
        if p:
            db.session.add(RolePermission(role_id=role_mgr.role_id, permission_id=p.permission_id))
    for code in staff_codes:
        p = Permission.query.filter_by(permission_code=code).first()
        if p:
            db.session.add(RolePermission(role_id=role_staff.role_id, permission_id=p.permission_id))

    # ── Positions ──
    from models.employee import Position
    pos_data = [
        ('收银员', '收银结算', 'C'), ('理货员', '货物整理', 'C'),
        ('采购员', '商品采购', 'B'), ('仓库管理员', '仓储管理', 'B'),
        ('店长', '门店管理', 'A'), ('会计', '财务管理', 'B'),
    ]
    positions = []
    for name, resp, grade in pos_data:
        pos = Position.query.filter_by(position_name=name).first()
        if not pos:
            pos = Position(position_name=name, responsibilities=resp, salary_grade=grade)
            db.session.add(pos)
        positions.append(pos)
    db.session.flush()

    # ── Employees ──
    emp_data = [
        ('王小明', 'EMP001', '采购部', 2, '2024-03-01'),
        ('李小红', 'EMP002', '仓储部', 3, '2024-06-15'),
        ('张大伟', 'EMP003', '销售部', 4, '2023-11-01'),
        ('赵丽丽', 'EMP004', '销售部', 0, '2025-01-10'),
        ('陈小华', 'EMP005', '仓储部', 1, '2025-04-20'),
    ]
    employees = []
    for name, no, dept, pi, hire in emp_data:
        e = Employee.query.filter_by(employee_no=no).first()
        if not e:
            e = Employee(employee_name=name, employee_no=no, department=dept,
                         position_id=positions[pi].position_id, phone=f'1390000{1000+len(employees)}',
                         status='active', hire_date=datetime.strptime(hire, '%Y-%m-%d').date())
            db.session.add(e)
        employees.append(e)
    db.session.flush()

    admin.employee_id = employees[2].employee_id
    zhangsan.employee_id = employees[0].employee_id
    lisi.employee_id = employees[3].employee_id

    # ── Categories ──
    from models.product import Category
    cat_names = ['生鲜果蔬', '粮油调味', '休闲食品', '酒水饮料', '日用百货', '乳制品', '冷冻食品', '个人护理', '家居清洁', '母婴用品']
    categories = []
    for i, name in enumerate(cat_names):
        c = Category.query.filter_by(category_name=name).first()
        if not c:
            c = Category(category_name=name, sort_order=i+1)
            db.session.add(c)
        categories.append(c)
    db.session.flush()

    # ── Suppliers ──
    from models.supplier import Supplier, SupplierContract, SupplierEvaluation
    sup_data = [
        ('鲜达供应链', '张经理', '13800001111', '上海市浦东新区', 'AAA'),
        ('绿源农业合作社', '李场长', '13800002222', '山东省寿光市', 'AA'),
        ('鼎丰粮油集团', '王总', '13800003333', '黑龙江省哈尔滨市', 'AAA'),
        ('海天味业', '赵经理', '13800004444', '广东省佛山市', 'AA'),
        ('统一食品', '钱经理', '13800005555', '江苏省昆山市', 'A'),
    ]
    suppliers = []
    for name, contact, phone, addr, credit in sup_data:
        s = Supplier.query.filter_by(supplier_name=name).first()
        if not s:
            s = Supplier(supplier_name=name, contact_person=contact, phone=phone, address=addr, credit_level=credit)
            db.session.add(s)
        suppliers.append(s)
    db.session.flush()

    for s in suppliers[:4]:
        db.session.add(SupplierContract(supplier_id=s.supplier_id, contract_number=f'HT-{s.supplier_id}-2026',
            contract_type='年度框架', start_date=date(2026,1,1), end_date=date(2026,12,31),
            total_amount=round(random.uniform(50000,300000),2), status='active'))
    for s in suppliers[:4]:
        db.session.add(SupplierEvaluation(supplier_id=s.supplier_id, evaluator_id=employees[2].employee_id,
            score=round(random.uniform(75,98),1), quality_score=round(random.uniform(70,99),1),
            delivery_score=round(random.uniform(70,99),1), service_score=round(random.uniform(70,99),1),
            evaluation_date=date.today(), comments='良好'))

    # ── Warehouses ──
    from models.warehouse import Warehouse
    wh_data = [('常温库-A区', '主仓一层A区', 5000), ('常温库-B区', '主仓一层B区', 3000),
               ('冷藏库', '地下冷库', 800), ('精品库', '主仓二层', 1200)]
    warehouses = []
    for name, loc, cap in wh_data:
        w = Warehouse.query.filter_by(warehouse_name=name).first()
        if not w:
            w = Warehouse(warehouse_name=name, location=loc, capacity=cap, status='active')
            db.session.add(w)
        warehouses.append(w)
    db.session.flush()

    # ── Products ──
    from models.product import Product
    prod_data = [
        ('红富士苹果', 0, 0, 8.5, '500g', '个'), ('猪五花肉', 1, 0, 28.0, '500g', '斤'),
        ('东北大米5kg', 2, 1, 42.0, '5kg', '袋'), ('金龙鱼调和油', 3, 1, 68.0, '5L', '桶'),
        ('乐事薯片原味', 4, 2, 7.5, '75g', '袋'), ('元气森林气泡水', 5, 3, 5.0, '480ml', '瓶'),
        ('青岛啤酒500ml', 6, 3, 8.0, '500ml', '罐'), ('妙洁保鲜袋', 7, 4, 12.9, '100只', '卷'),
        ('蒙牛纯牛奶', 8, 5, 6.5, '250ml', '盒'), ('思念水饺', 9, 6, 18.9, '500g', '袋'),
        ('飘柔洗发水', 10, 7, 32.0, '400ml', '瓶'), ('蓝月亮洗衣液', 11, 8, 28.5, '1kg', '瓶'),
        ('花王纸尿裤', 12, 9, 85.0, '54片', '包'),
    ]
    products = []
    for idx, (name, cat_i, sup_i, price, spec, unit) in enumerate(prod_data):
        p = Product.query.filter_by(product_name=name).first()
        if not p:
            p = Product(product_name=name, category_id=categories[cat_i].category_id,
                        supplier_id=suppliers[sup_i].supplier_id,
                        base_price=price, spec=spec, unit=unit, status='active')
            db.session.add(p)
        products.append(p)
    db.session.flush()

    # ── Inventory ──
    from models.warehouse import Inventory, InventoryDetail
    for idx, p in enumerate(products):
        wh = warehouses[idx % len(warehouses)]
        stock = random.randint(5, 45) if idx < 3 else random.randint(80, 500)
        status = 'low' if stock <= 50 else 'normal'
        db.session.add(Inventory(product_id=p.product_id, warehouse_id=wh.warehouse_id,
            stock_quantity=stock, safety_stock=50, status=status))
        db.session.add(InventoryDetail(warehouse_id=wh.warehouse_id, product_id=p.product_id,
            batch_no=f'BATCH{datetime.now().strftime("%y%m%d")}{idx+1:02d}',
            quantity=stock, bin_location=f'A-{idx+1:02d}', status='normal'))

    # ── Members ──
    from models.member import Member, MemberLevel, MemberPointsRecord, PointsPolicy
    lv_data = [('铜卡','消费满500',0.97), ('银卡','消费满2000',0.95),
               ('金卡','消费满5000',0.9), ('钻石卡','消费满20000',0.85)]
    for lv_name, cond, disc in lv_data:
        db.session.add(MemberLevel(level_name=lv_name, upgrade_condition=cond, discount_rate=disc,
            points_multiplier=1+random.random(), description=f'{lv_name}会员'))
    db.session.flush()

    mem_data = [('刘先生','13800001234','金卡',3200), ('陈女士','13800001235','银卡',1500),
                ('周先生','13800001236','铜卡',320), ('林女士','13800001237','银卡',2300),
                ('黄先生','13800001238','铜卡',120)]
    members = []
    for name, phone, level, pts in mem_data:
        m = Member.query.filter_by(member_name=name).first()
        if not m:
            m = Member(member_no=f'M{datetime.now().strftime("%y%m%d")}{random.randint(0,999999):06d}',
                       member_name=name, phone=phone, level=level, points=pts,
                       register_date=date.today()-timedelta(days=random.randint(30,365)), status='active')
            db.session.add(m)
        members.append(m)
    db.session.flush()

    db.session.add(PointsPolicy(policy_name='消费积分', earn_rule='每消费1元积1分',
        redeem_rule='100分抵1元', valid_period=365, status='active'))
    for m in members:
        db.session.add(MemberPointsRecord(member_id=m.member_id, points_change=random.choice([100,200,500]),
            change_type='consume', change_date=datetime.now()-timedelta(days=random.randint(1,30))))

    # ── Purchase Orders ──
    from models.purchase import PurchaseOrder, PurchaseOrderItem
    mgr_id = employees[2].employee_id
    for i in range(3):
        s = suppliers[i]
        wh = warehouses[i]
        po = PurchaseOrder(supplier_id=s.supplier_id, order_number=f'PO-202605-{i+1:03d}',
            order_date=date.today()-timedelta(days=random.randint(5,15)),
            total_amount=0, status='approved' if i<2 else 'pending',
            warehouse_id=wh.warehouse_id, created_by=mgr_id,
            delivery_date=date.today()+timedelta(days=random.randint(3,10)))
        db.session.add(po)
        db.session.flush()
        total = 0
        for j in range(random.randint(2,4)):
            p = products[(i+j) % len(products)]
            qty = random.randint(10,50)
            price = round(float(p.base_price) * random.uniform(0.6,0.8), 2)
            sub = round(qty * price, 2)
            total += sub
            db.session.add(PurchaseOrderItem(order_id=po.order_id, product_id=p.product_id,
                quantity=qty, unit_price=price, subtotal=sub))
        po.total_amount = round(total, 2)
        db.session.flush()

    # ── Sales Orders ──
    from models.sales import SalesOrder, SalesOrderItem
    from models.finance import CashRecord
    for i in range(7):
        days_ago = [0,1,2,5,8,0,15][i]
        od = datetime.now() - timedelta(days=days_ago)
        m = members[i % len(members)]
        emp = employees[i % len(employees)]
        so = SalesOrder(order_number=f'SO-202605-{i+1:03d}',
            member_id=m.member_id, employee_id=emp.employee_id,
            total_amount=0, payment_method=random.choice(['cash','wechat','alipay']),
            order_date=od, status='completed')
        db.session.add(so)
        db.session.flush()
        total = 0
        for j in range(random.randint(1,4)):
            p = products[(i+j) % len(products)]
            qty = random.randint(1,5)
            sub = round(qty * float(p.base_price), 2)
            total += sub
            db.session.add(SalesOrderItem(order_id=so.order_id, product_id=p.product_id,
                quantity=qty, unit_price=p.base_price, subtotal=sub))
        so.total_amount = round(total, 2)
        db.session.flush()
        db.session.add(CashRecord(order_id=so.order_id, employee_id=emp.employee_id,
            amount=so.total_amount, payment_method=so.payment_method,
            transaction_time=od, status='success'))

    # ── Finance ──
    from models.finance import Account, JournalEntry, JournalEntryItem, Budget, TaxDeclaration
    acct_data = [
        ('1001','库存现金','asset',50000), ('1002','银行存款','asset',350000),
        ('1401','库存商品','asset',120000), ('2201','应付账款','liability',80000),
        ('4001','主营业务收入','revenue',0), ('5001','主营业务成本','expense',0),
        ('5002','管理费用','expense',0), ('5003','销售费用','expense',0),
    ]
    accounts = []
    for code, name, atype, bal in acct_data:
        a = Account(account_code=code, account_name=name, account_type=atype, balance=bal)
        db.session.add(a)
        accounts.append(a)
    db.session.flush()

    je = JournalEntry(voucher_no='J-202605-001', entry_date=date.today(),
        description='支付供应商货款', total_debit=50000, total_credit=50000, created_by=mgr_id, status='posted')
    db.session.add(je)
    db.session.flush()
    db.session.add(JournalEntryItem(journal_entry_id=je.journal_entry_id, account_id=accounts[3].account_id,
        debit_amount=50000, credit_amount=0, description='冲减应付账款'))
    db.session.add(JournalEntryItem(journal_entry_id=je.journal_entry_id, account_id=accounts[1].account_id,
        debit_amount=0, credit_amount=50000, description='银行存款支付'))

    db.session.add(Budget(budget_period='2026-05', account_id=accounts[4].account_id,
        planned_amount=200000, actual_amount=185000, variance=15000, status='approved'))
    db.session.add(Budget(budget_period='2026-05', account_id=accounts[6].account_id,
        planned_amount=50000, actual_amount=42000, variance=8000, status='approved'))
    db.session.add(TaxDeclaration(tax_type='增值税', declaration_period='2026-04',
        tax_amount=15600, paid_amount=15600, payment_status='paid', submission_date=date(2026,5,10)))
    db.session.add(TaxDeclaration(tax_type='企业所得税', declaration_period='2026-Q1',
        tax_amount=28500, paid_amount=0, payment_status='unpaid'))

    # ── Sales Statistics ──
    from models.sales import SalesStatistic
    db.session.add(SalesStatistic(stat_period='2026-05', total_amount=185000,
        order_count=856, product_count=len(products)))

    # ── System Logs ──
    from models.system import SystemLog
    for log_type, mod, act in [('login','system','用户登录'), ('operation','product','新增商品'),
                               ('audit','finance','审批付款'), ('exception','purchase','采购异常')]:
        db.session.add(SystemLog(user_id=admin.user_id, log_type=log_type, module=mod, action=act,
            description=act, ip_address='127.0.0.1', log_time=datetime.now()-timedelta(hours=random.randint(1,48))))

    db.session.commit()
    print(f'[seed] Done! {Position.query.count()} positions, {products.__len__()} products, {members.__len__()} members, '
          f'{SalesOrder.query.count()} sales orders.')


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
