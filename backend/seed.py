"""生成测试数据"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from APP import app
from models import db
from models.user import User
from models.product import Category, Product, Promotion, PromotionProduct
from models.supplier import Supplier, SupplierContract, SupplierEvaluation
from models.purchase import PurchaseOrder, PurchaseOrderItem
from models.warehouse import Warehouse, Inventory, InventoryDetail, InboundRecord, InboundItem, OutboundRecord, OutboundItem
from models.sales import SalesOrder, SalesOrderItem, SalesReturn, SalesReturnItem, SalesStatistic
from models.member import Member, MemberLevel, MemberPointsRecord, PointsPolicy, MemberLevelPolicy
from models.employee import Position, Employee, Schedule, Attendance, Payroll
from models.finance import CashRecord, Account, JournalEntry, JournalEntryItem, Budget, TaxDeclaration
from models.system import Role, Permission, UserRole, RolePermission, SystemLog, BackupRecord, SystemConfig
from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash
import random

with app.app_context():
    # Ensure all tables exist (creates missing without dropping existing)
    db.create_all()
    print("All tables ensured.")

    # Delete all data in reverse FK-safe order
    delete_order = [
        SystemLog, BackupRecord, UserRole, RolePermission,
        Permission, SystemConfig,
        CashRecord,
        SalesReturnItem, SalesReturn, SalesOrderItem, SalesOrder,
        SalesStatistic,
        OutboundItem, OutboundRecord, InboundItem, InboundRecord,
        InventoryDetail, Inventory,
        PurchaseOrderItem, PurchaseOrder,
        PromotionProduct, Promotion, Product,
        MemberPointsRecord, MemberLevelPolicy, MemberLevel, PointsPolicy, Member,
        Payroll, Attendance, Schedule,
        SupplierEvaluation, SupplierContract,
        TaxDeclaration, Budget,
        JournalEntryItem, JournalEntry,
        Employee,
        Account, Category, Warehouse,
        Supplier, Position, Role,
        User,
    ]
    for model in delete_order:
        db.session.execute(model.__table__.delete())
    db.session.commit()
    print("All data deleted.")

    # ==================== System ====================
    admin = User(username='admin', password_hash=generate_password_hash('admin123'), status='active', last_login=datetime.now())
    user1 = User(username='zhangsan', password_hash=generate_password_hash('123456'), status='active')
    user2 = User(username='lisi', password_hash=generate_password_hash('123456'), status='active')
    db.session.add_all([admin, user1, user2])
    db.session.flush()

    role_admin = Role(role_name='系统管理员', description='全部权限')
    role_mgr = Role(role_name='经理', description='管理权限')
    role_staff = Role(role_name='员工', description='基础权限')
    db.session.add_all([role_admin, role_mgr, role_staff])
    db.session.flush()

    db.session.add_all([UserRole(user_id=admin.user_id, role_id=role_admin.role_id),
                         UserRole(user_id=user1.user_id, role_id=role_mgr.role_id),
                         UserRole(user_id=user2.user_id, role_id=role_staff.role_id)])

    all_perms_data = [
        # CRUD permissions
        ('sys:manage', '系统管理', 'system'), ('product:crud', '商品管理', 'product'), ('supplier:crud', '供应商管理', 'supplier'),
        ('purchase:crud', '采购管理', 'purchase'), ('warehouse:crud', '仓库管理', 'warehouse'), ('sales:crud', '销售管理', 'sales'),
        ('member:crud', '会员管理', 'member'), ('employee:crud', '人员管理', 'employee'), ('finance:crud', '财务管理', 'finance'),
        # Approval permissions
        ('purchase.approve', '采购审批', 'purchase'), ('sales.return.approve', '退货审批', 'sales'),
        ('finance.journal.post', '凭证过账', 'finance'), ('finance.budget.approve', '预算审批', 'finance'),
        ('employee.payroll.approve', '工资审批', 'employee'), ('system.user.manage', '用户管理', 'system'),
    ]
    perms = {}
    for code, name, module in all_perms_data:
        p = Permission(permission_code=code, permission_name=name, module=module)
        db.session.add(p)
        perms[code] = p
    db.session.flush()

    # Assign permissions to roles
    # Admin: ALL permissions
    for p in perms.values():
        db.session.add(RolePermission(role_id=role_admin.role_id, permission_id=p.permission_id))

    # Manager: all CRUD + approval (NOT sys:manage, NOT system.user.manage)
    mgr_codes = ['product:crud', 'supplier:crud', 'purchase:crud', 'warehouse:crud', 'sales:crud',
                 'member:crud', 'employee:crud', 'finance:crud',
                 'purchase.approve', 'sales.return.approve', 'finance.journal.post',
                 'finance.budget.approve', 'employee.payroll.approve']
    for code in mgr_codes:
        if code in perms:
            db.session.add(RolePermission(role_id=role_mgr.role_id, permission_id=perms[code].permission_id))

    # Staff: basic operations only, NO approvals
    staff_codes = ['product:crud', 'sales:crud', 'member:crud', 'warehouse:crud', 'purchase:crud']
    for code in staff_codes:
        if code in perms:
            db.session.add(RolePermission(role_id=role_staff.role_id, permission_id=perms[code].permission_id))

    SystemConfig.query.delete()
    configs = [
        SystemConfig(config_key='company_name', config_value='鲜丰超市', config_type='system', description='企业名称'),
        SystemConfig(config_key='tax_rate', config_value='0.13', config_type='business', description='增值税率'),
        SystemConfig(config_key='page_size', config_value='20', config_type='ui', description='每页条数'),
        SystemConfig(config_key='alert_threshold', config_value='50', config_type='business', description='库存预警阈值'),
    ]
    db.session.add_all(configs)

    # ==================== Categories ====================
    cats_data = ['生鲜果蔬', '粮油调味', '休闲食品', '酒水饮料', '日用百货', '乳制品', '冷冻食品', '个人护理', '家居清洁', '母婴用品']
    categories = []
    for i, name in enumerate(cats_data):
        c = Category(category_name=name, sort_order=i+1)
        db.session.add(c)
        categories.append(c)
    db.session.flush()

    # ==================== Suppliers ====================
    suppliers_data = [
        ('鲜达供应链', '张经理', '13800001111', '上海市浦东新区', 'AAA'),
        ('绿源农业合作社', '李场长', '13800002222', '山东省寿光市', 'AA'),
        ('鼎丰粮油集团', '王总', '13800003333', '黑龙江省哈尔滨市', 'AAA'),
        ('海天味业', '赵经理', '13800004444', '广东省佛山市', 'AA'),
        ('统一食品', '钱经理', '13800005555', '江苏省昆山市', 'A'),
    ]
    suppliers = []
    for name, contact, phone, addr, credit in suppliers_data:
        s = Supplier(supplier_name=name, contact_person=contact, phone=phone, address=addr, credit_level=credit)
        db.session.add(s)
        suppliers.append(s)
    db.session.flush()

    # Supplier Contracts (will be inserted after suppliers)
    for s in suppliers[:4]:
        db.session.add(SupplierContract(supplier_id=s.supplier_id, contract_number=f'HT-{s.supplier_id}-2026',
            contract_type='年度框架', start_date=date(2026,1,1), end_date=date(2026,12,31),
            total_amount=round(random.uniform(50000, 300000), 2), status='active'))

    # ==================== Positions & Employees ====================
    pos_data = [('收银员', '收银结算', 'C'), ('理货员', '货物整理', 'C'),
                ('采购员', '商品采购', 'B'), ('仓库管理员', '仓储管理', 'B'),
                ('店长', '门店管理', 'A')]
    positions = []
    for name, resp, grade in pos_data:
        p = Position(position_name=name, responsibilities=resp, salary_grade=grade)
        db.session.add(p)
        positions.append(p)
    db.session.flush()

    emp_data = [
        ('王小明', 'EMP001', '采购部', positions[2].position_id, 6500, '2024-03-01'),
        ('李小红', 'EMP002', '仓储部', positions[3].position_id, 5500, '2024-06-15'),
        ('张大伟', 'EMP003', '销售部', positions[4].position_id, 8500, '2023-11-01'),
        ('赵丽丽', 'EMP004', '销售部', positions[0].position_id, 4200, '2025-01-10'),
        ('陈小华', 'EMP005', '仓储部', positions[1].position_id, 3800, '2025-04-20'),
    ]
    employees = []
    for name, no, dept, pos_id, base, hire in emp_data:
        e = Employee(employee_name=name, employee_no=no, department=dept, position_id=pos_id,
                     phone=f'1390000{random.randint(1000,9999)}', status='active', hire_date=date.fromisoformat(hire))
        db.session.add(e)
        employees.append(e)
    db.session.flush()

    # Link users to employees
    admin.employee_id = employees[2].employee_id  # 张大伟 (店长)
    user1.employee_id = employees[0].employee_id  # 王小明 (采购员)
    user2.employee_id = employees[3].employee_id  # 赵丽丽 (收银员)
    db.session.flush()

    # Payrolls (generated_by references employee_id)
    mgr_id = employees[2].employee_id  # 张大伟 (店长)
    for e in employees:
        bonus = round(random.uniform(200, 1500), 2)
        ded = round(random.uniform(50, 300), 2)
        db.session.add(Payroll(employee_id=e.employee_id, pay_period='2026-05', base_salary=4800,
            bonus=bonus, deduction=ded, net_pay=4800+bonus-ded, status='pending', generated_by=mgr_id))

    # Supplier Evaluations (evaluator FK references employee)
    for s in suppliers[:4]:
        db.session.add(SupplierEvaluation(supplier_id=s.supplier_id, evaluator_id=mgr_id,
            score=round(random.uniform(70,99), 1), quality_score=round(random.uniform(70,99), 1),
            delivery_score=round(random.uniform(70,99), 1), service_score=round(random.uniform(70,99), 1),
            evaluation_date=date.today(), comments='良好'))

    # Schedules & Attendances
    for e in employees:
        for d_offset in range(0, 5):
            wd = date.today() - timedelta(days=d_offset)
            if wd.weekday() < 5:
                db.session.add(Schedule(employee_id=e.employee_id, work_date=wd, shift_type='morning',
                    start_time=time(8, 0), end_time=time(17, 0)))
                db.session.add(Attendance(employee_id=e.employee_id, check_in_time=datetime(wd.year,wd.month,wd.day,7,random.randint(45,59)),
                    check_out_time=datetime(wd.year,wd.month,wd.day,17,random.randint(0,15)), status='normal'))

    # ==================== Warehouses ====================
    wh_data = [('常温库-A区', '主仓一层A区', 5000), ('常温库-B区', '主仓一层B区', 3000),
               ('冷藏库', '地下冷库', 800), ('精品库', '主仓二层', 1200)]
    warehouses = []
    for name, loc, cap in wh_data:
        w = Warehouse(warehouse_name=name, location=loc, capacity=cap, status='active')
        db.session.add(w)
        warehouses.append(w)
    db.session.flush()

    # ==================== Products ====================
    products_data = [
        ('红富士苹果', 0, 8.5, '500g', '个'), ('猪五花肉', 0, 28.0, '500g', '斤'),
        ('东北大米5kg', 2, 42.0, '5kg', '袋'), ('金龙鱼调和油', 2, 68.0, '5L', '桶'),
        ('乐事薯片原味', 4, 7.5, '75g', '袋'), ('元气森林气泡水', 4, 5.0, '480ml', '瓶'),
        ('青岛啤酒500ml', 3, 8.0, '500ml', '罐'), ('妙洁保鲜袋', 0, 12.9, '100只', '卷'),
        ('蒙牛纯牛奶', 0, 6.5, '250ml', '盒'), ('思念水饺', 1, 18.9, '500g', '袋'),
        ('飘柔洗发水', 3, 32.0, '400ml', '瓶'), ('蓝月亮洗衣液', 3, 28.5, '1kg', '瓶'),
        ('花王纸尿裤', 0, 85.0, '54片', '包'),
    ]
    for i, pd in enumerate(products_data):
        sid = suppliers[pd[1]].supplier_id if pd[1] < len(suppliers) else suppliers[0].supplier_id
        cid = categories[i % len(categories)].category_id
        prod = Product(product_name=pd[0], category_id=cid, supplier_id=sid,
                       base_price=pd[2], spec=pd[3], unit=pd[4], status='active')
        db.session.add(prod)
    db.session.flush()

    # Get actual products for subsequent use
    all_products = Product.query.all()

    # ==================== Inventory ====================
    for idx, p in enumerate(all_products):
        wh_idx = random.randint(0, min(2, len(warehouses)-1))
        wh = warehouses[wh_idx] if wh_idx < len(warehouses) else warehouses[0]
        # First 3 products get low stock to demonstrate alerts
        if idx < 3:
            stock = random.randint(5, 45)
        else:
            stock = random.randint(50, 500)
        status = 'normal' if stock > 50 else ('out_of_stock' if stock <= 0 else 'low')
        db.session.add(Inventory(product_id=p.product_id, warehouse_id=wh.warehouse_id,
            stock_quantity=stock, safety_stock=50, status=status))
        db.session.add(InventoryDetail(warehouse_id=wh.warehouse_id, product_id=p.product_id,
            batch_no=f'BATCH{datetime.now().strftime("%y%m%d")}-{random.randint(100,999)}',
            quantity=stock, bin_location=f'A-{random.randint(1,20):02d}', status='normal'))

    # ==================== Members ====================
    levels = []
    for lv_name, cond, disc in [('铜卡', '消费满500', 0.97), ('银卡', '消费满2000', 0.95),
                                  ('金卡', '消费满5000', 0.9), ('钻石卡', '消费满20000', 0.85)]:
        lv = MemberLevel(level_name=lv_name, upgrade_condition=cond, discount_rate=disc,
                         points_multiplier=1+random.random(), description=f'{lv_name}会员')
        db.session.add(lv)
        levels.append(lv)
    db.session.flush()

    members_data = [('刘先生', '13800001234', '金卡', 3200), ('陈女士', '13800001235', '银卡', 1500),
                    ('周先生', '13800001236', '铜卡', 320), ('林女士', '13800001237', '银卡', 2300),
                    ('黄先生', '13800001238', '铜卡', 120)]
    members = []
    for name, phone, level, pts in members_data:
        m = Member(member_no=f'M{datetime.now().strftime("%y%m%d")}{random.randint(0,999999):06d}',
                   member_name=name, phone=phone, level=level, points=pts,
                   register_date=date.today()-timedelta(days=random.randint(30,365)), status='active')
        db.session.add(m)
        members.append(m)
    db.session.flush()

    # Points policies
    db.session.add(PointsPolicy(policy_name='消费积分', earn_rule='每消费1元积1分',
        redeem_rule='100分抵1元', valid_period=365, status='active'))
    db.session.add(PointsPolicy(policy_name='生日双倍', earn_rule='生日当天消费双倍积分',
        redeem_rule='不可单独兑现', valid_period=365, status='active'))

    # Points records
    for m in members:
        db.session.add(MemberPointsRecord(member_id=m.member_id, points_change=random.choice([100,200,500]),
            change_type='consume', change_date=datetime.now()-timedelta(days=random.randint(1,30))))

    # ==================== Purchase Orders & Inbound ====================
    for i in range(3):
        s = suppliers[i % len(suppliers)] if suppliers else suppliers[0]
        wh = warehouses[i % len(warehouses)] if warehouses else warehouses[0]
        po = PurchaseOrder(supplier_id=s.supplier_id, order_number=f'PO-202605-{i+1:03d}',
            order_date=date.today()-timedelta(days=random.randint(5,15)),
            total_amount=0, status='approved' if i<2 else 'pending',
            warehouse_id=wh.warehouse_id, created_by=mgr_id,
            delivery_date=date.today()+timedelta(days=random.randint(3,10)))
        db.session.add(po)
        db.session.flush()

        total = 0
        for j in range(random.randint(2,4)):
            p = all_products[(i+j) % len(all_products)] if all_products else None
            if p:
                qty = random.randint(10,50)
                price = round(float(p.base_price) * random.uniform(0.6, 0.8), 2)
                sub = round(qty * price, 2)
                total += sub
                db.session.add(PurchaseOrderItem(order_id=po.order_id, product_id=p.product_id,
                    quantity=qty, unit_price=price, subtotal=sub))

                # Inbound for approved orders (one per item)
                if po.status == 'approved':
                    ir = InboundRecord(inbound_no=f'IN-202605-{i+1:03d}-{j+1}', supplier_id=s.supplier_id,
                        warehouse_id=wh.warehouse_id, total_quantity=qty, inbound_date=datetime.now(),
                        status='completed', created_by=mgr_id)
                    db.session.add(ir)
                    db.session.flush()
                    db.session.add(InboundItem(inbound_record_id=ir.inbound_record_id, product_id=p.product_id,
                        batch_no=f'BATCH{datetime.now().strftime("%y%m%d")}{i+1:02d}{j+1}', quantity=qty,
                        unit_price=price, bin_location=f'B-{random.randint(1,15):02d}'))

        po.total_amount = round(total, 2)

    # ==================== Sales Orders ====================
    order_dates = [
        datetime.now(),  # today
        datetime.now() - timedelta(days=1),   # yesterday
        datetime.now() - timedelta(days=2),
        datetime.now() - timedelta(days=5),
        datetime.now() - timedelta(days=8),
        datetime.now(),  # another today order
        datetime.now() - timedelta(days=15),
    ]
    for i, od in enumerate(order_dates):
        m = members[i % len(members)] if members else None
        emp = employees[i % len(employees)] if employees else None
        so = SalesOrder(order_number=f'SO-202605-{i+1:03d}',
            member_id=m.member_id if m else None,
            employee_id=emp.employee_id if emp else employees[0].employee_id if employees else 1,
            total_amount=0, payment_method=random.choice(['cash','wechat','alipay']),
            order_date=od, status='completed')
        db.session.add(so)
        db.session.flush()

        total = 0
        for j in range(random.randint(1,4)):
            p = all_products[(i+j) % len(all_products)] if all_products else None
            if p:
                qty = random.randint(1,5)
                sub = round(qty * p.base_price, 2)
                total += sub
                db.session.add(SalesOrderItem(order_id=so.order_id, product_id=p.product_id,
                    quantity=qty, unit_price=p.base_price, subtotal=sub))

        so.total_amount = round(total, 2)

        # Cash record for each sale
        db.session.add(CashRecord(order_id=so.order_id, employee_id=so.employee_id,
            amount=so.total_amount, payment_method=so.payment_method,
            transaction_time=so.order_date, status='success'))

    # Sales Return
    so1 = SalesOrder.query.first()
    if so1:
        sr = SalesReturn(original_order_id=so1.order_id,
            member_id=so1.member_id, employee_id=so1.employee_id,
            return_amount=round(float(so1.total_amount) * 0.3, 2),
            reason='商品损坏', return_date=datetime.now(), status='completed')
        db.session.add(sr)

    # ==================== Promotions ====================
    prom = Promotion(promotion_name='五一特惠', promotion_type='discount', discount_rate=0.85,
        start_date=datetime(2026,5,20), end_date=datetime(2026,6,5), status='active')
    db.session.add(prom)
    db.session.flush()

    for p in all_products[:3]:
        db.session.add(PromotionProduct(promotion_id=prom.promotion_id, product_id=p.product_id, specific_discount=0.9))

    # ==================== Finance ====================
    # Accounts (Chart of Accounts)
    acct_data = [
        ('1001', '库存现金', 'asset', 50000), ('1002', '银行存款', 'asset', 350000),
        ('1401', '库存商品', 'asset', 120000), ('2201', '应付账款', 'liability', 80000),
        ('4001', '主营业务收入', 'revenue', 0), ('5001', '主营业务成本', 'expense', 0),
        ('5002', '管理费用', 'expense', 0), ('5003', '销售费用', 'expense', 0),
    ]
    accounts = []
    for code, name, atype, bal in acct_data:
        a = Account(account_code=code, account_name=name, account_type=atype, balance=bal)
        db.session.add(a)
        accounts.append(a)
    db.session.flush()

    # Journal Entry
    je = JournalEntry(voucher_no=f'J-202605-001', entry_date=date.today(),
        description='支付供应商货款', total_debit=50000, total_credit=50000,
        created_by=mgr_id, status='posted')
    db.session.add(je)
    db.session.flush()
    db.session.add(JournalEntryItem(journal_entry_id=je.journal_entry_id, account_id=accounts[3].account_id,
        debit_amount=50000, credit_amount=0, description='冲减应付账款'))
    db.session.add(JournalEntryItem(journal_entry_id=je.journal_entry_id, account_id=accounts[1].account_id,
        debit_amount=0, credit_amount=50000, description='银行存款支付'))

    # Budget
    db.session.add(Budget(budget_period='2026-05', account_id=accounts[4].account_id,
        planned_amount=200000, actual_amount=185000, variance=15000, status='approved'))
    db.session.add(Budget(budget_period='2026-05', account_id=accounts[6].account_id,
        planned_amount=50000, actual_amount=42000, variance=8000, status='approved'))

    # Tax
    db.session.add(TaxDeclaration(tax_type='增值税', declaration_period='2026-04',
        tax_amount=15600, paid_amount=15600, payment_status='paid', submission_date=date(2026,5,10)))
    db.session.add(TaxDeclaration(tax_type='企业所得税', declaration_period='2026-Q1',
        tax_amount=28500, paid_amount=0, payment_status='unpaid'))

    # ==================== Sales Statistics ====================
    db.session.add(SalesStatistic(stat_period='2026-05', total_amount=185000,
        order_count=856, product_count=len(all_products)))
    # ==================== System Logs & Backup ====================
    for log_type, mod, act in [('login','system','用户登录'), ('operation','product','新增商品'),
                                ('audit','finance','审批付款'), ('exception','purchase','采购异常')]:
        db.session.add(SystemLog(user_id=admin.user_id, log_type=log_type, module=mod, action=act,
            description=act, ip_address='127.0.0.1', log_time=datetime.now()-timedelta(hours=random.randint(1,48))))

    db.session.add(BackupRecord(backup_type='full', backup_path='/backups/db_20260525_0300.sql',
        backup_size=20480000, status='success', backup_time=datetime(2026,5,25,3,0,0)))

    db.session.commit()
    print("Seed data inserted successfully!")

    # Summary
    print(f"\n--- Summary ---")
    print(f"Users: {User.query.count()}")
    print(f"Roles: {Role.query.count()}")
    print(f"Categories: {Category.query.count()}")
    print(f"Suppliers: {Supplier.query.count()}")
    print(f"Products: {Product.query.count()}")
    print(f"Warehouses: {Warehouse.query.count()}")
    print(f"Inventory: {Inventory.query.count()}")
    print(f"Members: {Member.query.count()}")
    print(f"Employees: {Employee.query.count()}")
    print(f"Sales Orders: {SalesOrder.query.count()}")
    print(f"Purchase Orders: {PurchaseOrder.query.count()}")
    print(f"Accounts: {Account.query.count()}")
    print(f"\nCredentials: admin/admin123, zhangsan/123456, lisi/123456")
