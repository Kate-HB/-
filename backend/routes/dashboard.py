from flask import Blueprint, request, jsonify
from models import db
from models.sales import SalesOrder
from models.warehouse import Inventory
from models.member import Member
from models.purchase import PurchaseOrder
from models.sales import SalesReturn
from models.finance import Budget
from models.system import SystemLog
from utils.errors import success_response, error_response
from utils.auth import require_auth
from sqlalchemy import func
from datetime import date, timedelta

bp = Blueprint('dashboard', __name__)


@bp.route('/api/dashboard/kpi', methods=['GET'])
@require_auth
def dashboard_kpi():
    today = date.today()
    this_month_start = today.replace(day=1)

    today_sales = db.session.query(func.coalesce(func.sum(SalesOrder.total_amount), 0))\
        .filter(func.date(SalesOrder.order_date) == today, SalesOrder.status == 'completed')\
        .scalar()

    today_orders = db.session.query(func.count(SalesOrder.order_id))\
        .filter(func.date(SalesOrder.order_date) == today, SalesOrder.status == 'completed')\
        .scalar()

    month_sales = db.session.query(func.coalesce(func.sum(SalesOrder.total_amount), 0))\
        .filter(func.date(SalesOrder.order_date) >= this_month_start, SalesOrder.status == 'completed')\
        .scalar()

    inventory_alerts = Inventory.query.filter(
        Inventory.stock_quantity <= Inventory.safety_stock
    ).count()

    active_members = Member.query.filter(Member.status == 'active').count()

    pending_approvals = PurchaseOrder.query.filter(PurchaseOrder.status == 'pending').count() \
        + SalesReturn.query.filter(SalesReturn.status == 'pending').count() \
        + Budget.query.filter(Budget.status == 'draft').count()

    return jsonify(success_response({
        'today_sales': float(today_sales),
        'today_orders': today_orders,
        'month_sales': float(month_sales),
        'inventory_alerts': inventory_alerts,
        'active_members': active_members,
        'pending_approvals': pending_approvals
    }))


@bp.route('/api/dashboard/charts', methods=['GET'])
@require_auth
def dashboard_charts():
    today = date.today()

    # Sales trend: last 7 days
    trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        total = db.session.query(func.coalesce(func.sum(SalesOrder.total_amount), 0))\
            .filter(func.date(SalesOrder.order_date) == d, SalesOrder.status == 'completed')\
            .scalar()
        count = db.session.query(func.count(SalesOrder.order_id))\
            .filter(func.date(SalesOrder.order_date) == d, SalesOrder.status == 'completed')\
            .scalar()
        trend.append({
            'date': d.isoformat(),
            'label': d.strftime('%m/%d'),
            'amount': float(total),
            'orders': count
        })

    # Top selling products (from ranking table or aggregate sales items)
    from models.sales import SalesOrderItem
    top_products = db.session.query(
        SalesOrderItem.product_id,
        func.sum(SalesOrderItem.quantity).label('total_qty'),
        func.sum(SalesOrderItem.subtotal).label('total_amount')
    ).group_by(SalesOrderItem.product_id)\
     .order_by(func.sum(SalesOrderItem.subtotal).desc()).limit(10).all()

    top_result = []
    for p in top_products:
        from models.product import Product
        prod = Product.query.get(p.product_id)
        top_result.append({
            'product_id': p.product_id,
            'product_name': prod.product_name if prod else '未知商品',
            'total_quantity': int(p.total_qty),
            'total_amount': float(p.total_amount)
        })

    # Low stock items
    low_stock = Inventory.query.filter(
        Inventory.stock_quantity <= Inventory.safety_stock
    ).limit(10).all()

    low_result = []
    for inv in low_stock:
        from models.product import Product
        prod = Product.query.get(inv.product_id)
        low_result.append({
            'product_id': inv.product_id,
            'product_name': prod.product_name if prod else '未知商品',
            'stock_quantity': inv.stock_quantity,
            'safety_stock': inv.safety_stock,
            'warehouse_id': inv.warehouse_id
        })

    return jsonify(success_response({
        'sales_trend': trend,
        'top_products': top_result,
        'low_stock': low_result
    }))


@bp.route('/api/dashboard/notifications', methods=['GET'])
@require_auth
def dashboard_notifications():
    logs = SystemLog.query.order_by(SystemLog.log_time.desc()).limit(5).all()
    result = [{
        'log_id': r.log_id,
        'log_type': r.log_type,
        'module': r.module,
        'action': r.action,
        'description': r.description,
        'log_time': r.log_time.isoformat() if r.log_time else None
    } for r in logs]

    today = date.today()
    recent_orders = db.session.query(func.count(SalesOrder.order_id))\
        .filter(func.date(SalesOrder.order_date) == today)\
        .scalar()

    low_stock_products = Inventory.query.filter(
        Inventory.status.in_(['low', 'out_of_stock'])
    ).count()

    result.insert(0, {
        'log_id': 0,
        'log_type': 'operation',
        'module': 'dashboard',
        'action': 'summary',
        'description': f'今日订单数: {recent_orders}, 低库存商品: {low_stock_products}',
        'log_time': today.isoformat()
    })

    return jsonify(success_response(result))
