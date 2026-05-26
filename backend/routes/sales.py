from flask import Blueprint, request, jsonify
from models import db
from models.sales import SalesOrder, SalesOrderItem, SalesReturn, SalesReturnItem, SalesStatistic
from models.warehouse import Inventory, Warehouse
from models.finance import CashRecord
from models.product import Product, Promotion, PromotionProduct
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime, date
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import uuid

bp = Blueprint('sales', __name__)


# ==================== Sales Orders ====================

@bp.route('/api/sales-orders', methods=['GET'])
@require_auth
def get_sales_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    period = request.args.get('period', '').strip()

    q = SalesOrder.query
    if status:
        q = q.filter(SalesOrder.status == status)
    if search:
        q = q.filter(SalesOrder.order_number.contains(search))
    if period:
        df = build_sales_date_filter(period)
        if df is not None:
            q = q.filter(df)

    total = q.count()
    rows = q.options(
        joinedload(SalesOrder.member),
        joinedload(SalesOrder.employee),
        joinedload(SalesOrder.items).joinedload(SalesOrderItem.product)
    ).order_by(SalesOrder.order_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'order_id': r.order_id,
        'order_number': r.order_number,
        'member_id': r.member_id,
        'member_name': r.member.member_name if r.member else '',
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'total_amount': float(r.total_amount),
        'discount_amount': float(r.discount_amount) if r.discount_amount else 0,
        'amount_received': float(r.amount_received) if r.amount_received else None,
        'change_amount': float(r.change_amount) if r.change_amount else 0,
        'payment_method': r.payment_method,
        'order_date': r.order_date.isoformat() if r.order_date else None,
        'status': r.status,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.product_name,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'subtotal': float(item.subtotal)
        } for item in r.items]
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/sales-orders/<int:id>', methods=['GET'])
@require_auth
def get_sales_order(id):
    r = SalesOrder.query.options(
        joinedload(SalesOrder.member),
        joinedload(SalesOrder.employee),
        joinedload(SalesOrder.items).joinedload(SalesOrderItem.product)
    ).get_or_404(id)
    result = {
        'order_id': r.order_id,
        'order_number': r.order_number,
        'member_id': r.member_id,
        'member_name': r.member.member_name if r.member else '',
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'total_amount': float(r.total_amount),
        'discount_amount': float(r.discount_amount) if r.discount_amount else 0,
        'amount_received': float(r.amount_received) if r.amount_received else None,
        'change_amount': float(r.change_amount) if r.change_amount else 0,
        'payment_method': r.payment_method,
        'order_date': r.order_date.isoformat() if r.order_date else None,
        'status': r.status,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.product_name,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'subtotal': float(item.subtotal)
        } for item in r.items]
    }
    return jsonify(success_response(result))


@bp.route('/api/sales-orders', methods=['POST'])
@require_auth
@require_permission('sales:crud')
def add_sales_order():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_id')
    if missing: return error_response(f'缺少必填字段: {missing}')
    order = SalesOrder(
        order_number=data.get('order_number', 'SO' + datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:4].upper()),
        member_id=data.get('member_id'),
        employee_id=data['employee_id'],
        total_amount=data.get('total_amount', 0),
        payment_method=data.get('payment_method', ''),
        status=data.get('status', 'completed')
    )
    db.session.add(order)
    db.session.flush()

    items = data.get('items', [])
    if not items:
        return error_response('订单明细不能为空')
    total = 0
    for item in items:
        if not item.get('product_id') or not item.get('quantity'):
            return error_response('明细缺少商品或数量')
        subtotal = int(item['quantity']) * float(item['unit_price'])
        total += subtotal
        oi = SalesOrderItem(
            order_id=order.order_id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            subtotal=subtotal
        )
        db.session.add(oi)

        total_stock = db.session.query(func.coalesce(func.sum(Inventory.stock_quantity), 0))\
            .filter(Inventory.product_id == item['product_id']).scalar()
        if total_stock < item['quantity']:
            db.session.rollback()
            return error_response(f'商品 {item["product_id"]} 库存不足')
        inv = Inventory.query.filter_by(product_id=item['product_id'])\
            .filter(Inventory.stock_quantity >= item['quantity']).first()
        if not inv:
            inv = Inventory.query.filter_by(product_id=item['product_id'])\
                .order_by(Inventory.stock_quantity.desc()).first()
        if not inv:
            db.session.rollback()
            return error_response(f'商品 {item["product_id"]} 无库存记录')
        if inv.stock_quantity < item['quantity']:
            db.session.rollback()
            return error_response(f'商品 {item["product_id"]} 库存不足')
        inv.stock_quantity -= item['quantity']

    order.total_amount = total
    db.session.commit()
    log_operation('sales', 'create', 'SalesOrder', order.order_id, data.get('order_number', ''))
    return jsonify(success_response({'order_id': order.order_id}, '销售订单创建成功'))


@bp.route('/api/sales-orders/<int:id>', methods=['PUT'])
@require_auth
@require_permission('sales:crud')
def update_sales_order(id):
    order = SalesOrder.query.get_or_404(id)
    if order.status not in ('draft', 'pending'):
        return error_response('只能修改草稿或待处理状态的订单')
    data, err = get_json()
    if err: return err
    for field in ['member_id', 'payment_method', 'status']:
        if field in data:
            setattr(order, field, data[field])
    if 'items' in data:
        SalesOrderItem.query.filter_by(order_id=id).delete()
        total = 0
        for item in data['items']:
            if not item.get('product_id') or not item.get('quantity'):
                return error_response('明细缺少商品或数量')
            qty = int(item['quantity'])
            price = float(item.get('unit_price', 0))
            subtotal = qty * price
            total += subtotal
            oi = SalesOrderItem(order_id=id, product_id=item['product_id'], quantity=qty, unit_price=price, subtotal=subtotal)
            db.session.add(oi)
        order.total_amount = total
    db.session.commit()
    log_operation('sales', 'update', 'SalesOrder', id, data.get('order_number') or order.order_number)
    return jsonify(success_response(message='订单更新成功'))


@bp.route('/api/sales-orders/<int:id>/cancel', methods=['PUT'])
@require_auth
@require_permission('sales:crud')
def cancel_sales_order(id):
    order = SalesOrder.query.get_or_404(id)
    if order.status == 'cancelled':
        return error_response('订单已取消')
    if order.status == 'refunded':
        return error_response('已退款订单不可取消')
    for item in order.items:
        inv = Inventory.query.filter_by(product_id=item.product_id).first()
        if inv:
            inv.stock_quantity += item.quantity
        else:
            wh = Warehouse.query.first()
            if not wh:
                db.session.rollback()
                return error_response('无可用仓库')
            inv = Inventory(product_id=item.product_id, warehouse_id=wh.warehouse_id, stock_quantity=item.quantity)
            db.session.add(inv)
    order.status = 'cancelled'
    db.session.commit()
    log_operation('sales', 'cancel', 'SalesOrder', id, data.get('order_number') or order.order_number)
    return jsonify(success_response(message='订单已取消，库存已恢复'))


# ==================== Cash Register (POS) ====================

@bp.route('/api/cash-register', methods=['POST'])
@require_auth
@require_permission('sales:crud')
def cash_register():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_id', 'payment_method', 'amount_received')
    if missing: return error_response(f'缺少必填字段: {missing}')
    items = data.get('items', [])
    if not items:
        return error_response('订单明细不能为空')

    now = datetime.utcnow()
    product_ids = [int(item['product_id']) for item in items]

    # Look up active promotions linked to these products
    product_promo_rows = db.session.query(Promotion, PromotionProduct).join(
        PromotionProduct, Promotion.promotion_id == PromotionProduct.promotion_id
    ).filter(
        PromotionProduct.product_id.in_(product_ids),
        Promotion.status == 'active',
        Promotion.start_date <= now,
        Promotion.end_date >= now
    ).all()

    # Also look up active store-wide promotions (not linked to specific products)
    linked_promo_ids = {p.promotion_id for p, _ in product_promo_rows}
    store_q = Promotion.query.filter(
        Promotion.status == 'active',
        Promotion.start_date <= now,
        Promotion.end_date >= now
    )
    if linked_promo_ids:
        store_q = store_q.filter(~Promotion.promotion_id.in_(linked_promo_ids))
    store_promos = store_q.all()

    # Build: product_id -> list of (promotion, promotion_product)
    promo_map = {}
    for promo, pp in product_promo_rows:
        promo_map.setdefault(pp.product_id, []).append((promo, pp))
    # Store-wide promotions apply to all products
    for promo in store_promos:
        for pid in product_ids:
            promo_map.setdefault(pid, []).append((promo, None))

    applied_names = set()
    item_discounts = {}  # product_id -> discount amount per unit
    total_discount = 0

    # Calculate item-level discounts (discount type)
    for item in items:
        pid = int(item['product_id'])
        qty = int(item['quantity'])
        original_price = float(item.get('unit_price', 0))
        final_price = original_price

        for promo, pp in promo_map.get(pid, []):
            if promo.promotion_type == 'discount':
                specific = float(pp.specific_discount) if pp and pp.specific_discount else None
                rate = float(specific or promo.discount_rate or 1)
                if 0 < rate < 1:
                    final_price = min(final_price, round(original_price * rate, 2))
                    applied_names.add(promo.promotion_name)

        if final_price < original_price:
            discount_per_unit = round(original_price - final_price, 2)
            item_discounts[pid] = discount_per_unit
            total_discount += qty * discount_per_unit

    # Calculate subtotal with discounts
    total = 0
    for item in items:
        qty = int(item['quantity'])
        original_price = float(item.get('unit_price', 0))
        discount = item_discounts.get(int(item['product_id']), 0)
        final_price = original_price - discount
        total += qty * final_price

    # Apply full_reduction promotions (check min_amount threshold)
    full_reduction = 0
    for item in items:
        for promo, pp in promo_map.get(int(item['product_id']), []):
            if promo.promotion_type == 'full_reduction' and promo.fixed_amount:
                threshold = float(promo.min_amount or 0)
                if total >= threshold:
                    amount = float(promo.fixed_amount)
                    if amount > full_reduction:
                        full_reduction = amount
                        applied_names.add(promo.promotion_name)
    if full_reduction > total:
        full_reduction = 0
    total = round(total - full_reduction, 2)
    total_discount = round(total_discount + full_reduction, 2)

    # Apply buy_gift promotions (check min_quantity threshold, use gift_quantity)
    gift_items = []
    seen_gift_promos = set()
    cart_qty_map = {int(item['product_id']): int(item['quantity']) for item in items}
    for item in items:
        pid = int(item['product_id'])
        for promo, pp in promo_map.get(pid, []):
            if promo.promotion_type == 'buy_gift' and promo.gift_product_id and promo.promotion_id not in seen_gift_promos:
                # Sum quantities of all cart items linked to this promo
                promo_linked_pids = {p for p, promos in promo_map.items()
                                     if any(p2.promotion_id == promo.promotion_id for p2, _ in promos)}
                linked_qty = sum(cart_qty_map.get(p, 0) for p in promo_linked_pids) if promo_linked_pids else cart_qty_map.get(pid, 0)
                min_qty = promo.min_quantity or 1
                if linked_qty >= min_qty:
                    seen_gift_promos.add(promo.promotion_id)
                    gift = Product.query.get(promo.gift_product_id)
                    if gift:
                        gift_qty = promo.gift_quantity or 1
                        gift_items.append({
                            'product_id': gift.product_id,
                            'product_name': gift.product_name,
                            'quantity': gift_qty,
                            'unit_price': 0
                        })
                        applied_names.add(promo.promotion_name)

    # Calculate member points (1 yuan = 1 point baseline, points promo multiplies)
    points_earned = 0
    if data.get('member_id'):
        points_multiplier = 1.0
        all_promos = [p for p, _ in product_promo_rows] + list(store_promos)
        for promo in all_promos:
            if promo.promotion_type == 'points' and promo.discount_rate:
                points_multiplier = max(points_multiplier, float(promo.discount_rate))
        points_earned = int(total * points_multiplier)

    amount_received = float(data['amount_received'])
    if amount_received < total:
        return error_response(f'收款金额不足，应收 {total}，实收 {amount_received}')

    for item in items + gift_items:
        total_stock = db.session.query(func.coalesce(func.sum(Inventory.stock_quantity), 0))\
            .filter(Inventory.product_id == item['product_id']).scalar()
        if total_stock < int(item['quantity']):
            return error_response(f'商品 {item["product_id"]} 库存不足')

    order = SalesOrder(
        order_number=data.get('order_number', 'SO' + datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:4].upper()),
        member_id=data.get('member_id'),
        employee_id=data['employee_id'],
        total_amount=total,
        discount_amount=total_discount,
        amount_received=amount_received,
        change_amount=round(amount_received - total, 2),
        payment_method=data['payment_method'],
        status='completed'
    )
    db.session.add(order)
    db.session.flush()

    for item in items + gift_items:
        qty = int(item['quantity'])
        original_price = float(item.get('unit_price', 0))
        discount = item_discounts.get(int(item['product_id']), 0)
        final_price = round(original_price - discount, 2)
        subtotal = qty * final_price
        oi = SalesOrderItem(
            order_id=order.order_id,
            product_id=item['product_id'],
            quantity=qty,
            unit_price=final_price,
            subtotal=subtotal
        )
        db.session.add(oi)

        inv = Inventory.query.filter_by(product_id=item['product_id'])\
            .filter(Inventory.stock_quantity >= qty).first()
        if not inv:
            inv = Inventory.query.filter_by(product_id=item['product_id'])\
                .order_by(Inventory.stock_quantity.desc()).first()
        if not inv:
            db.session.rollback()
            return error_response(f'商品 {item["product_id"]} 无库存记录')
        if inv.stock_quantity < qty:
            db.session.rollback()
            return error_response(f'商品 {item["product_id"]} 库存不足')
        inv.stock_quantity -= qty

    # Award member points
    if points_earned > 0:
        from models.member import Member, MemberPointsRecord
        member = Member.query.get(int(data['member_id']))
        if member:
            member.points = (member.points or 0) + points_earned
            db.session.add(MemberPointsRecord(
                member_id=member.member_id,
                points_change=points_earned,
                change_type='consume',
                change_date=datetime.utcnow(),
                description=f'消费奖励 {points_earned} 积分'
            ))

    cr = CashRecord(
        order_id=order.order_id,
        employee_id=data['employee_id'],
        amount=amount_received,
        payment_method=data['payment_method'],
        transaction_time=datetime.utcnow(),
        status='completed'
    )
    db.session.add(cr)
    db.session.commit()
    log_operation('sales', 'create', 'SalesOrder', order.order_id, order.order_number)

    return jsonify(success_response({
        'order_id': order.order_id,
        'order_number': order.order_number,
        'total_amount': total,
        'amount_received': amount_received,
        'change': round(amount_received - total, 2),
        'payment_method': data['payment_method'],
        'order_date': order.order_date.isoformat() if order.order_date else None,
        'promotions': list(applied_names),
        'total_discount': total_discount,
        'points_earned': points_earned
    }, '收银成功'))


# ==================== Sales Returns ====================

@bp.route('/api/sales-returns', methods=['GET'])
@require_auth
def get_sales_returns():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    q = SalesReturn.query
    total = q.count()
    rows = q.options(
        joinedload(SalesReturn.member),
        joinedload(SalesReturn.employee),
        joinedload(SalesReturn.items).joinedload(SalesReturnItem.product)
    ).order_by(SalesReturn.return_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'return_id': r.return_id,
        'original_order_id': r.original_order_id,
        'member_id': r.member_id,
        'member_name': r.member.member_name if r.member else '',
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'return_amount': float(r.return_amount),
        'reason': r.reason,
        'return_date': r.return_date.isoformat() if r.return_date else None,
        'status': r.status,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.product_name,
            'quantity': item.quantity,
            'refund_amount': float(item.refund_amount)
        } for item in r.items]
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/sales-returns', methods=['POST'])
@require_auth
@require_permission('sales:crud')
def add_sales_return():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'original_order_id', 'employee_id')
    if missing: return error_response(f'缺少必填字段: {missing}')
    items_data = data.get('items', [])
    if not items_data:
        return error_response('退货明细不能为空')

    original_order = SalesOrder.query.options(joinedload(SalesOrder.items)).get(data['original_order_id'])
    if not original_order:
        return error_response('原订单不存在')
    if original_order.status == 'refunded':
        return error_response('原订单已全额退款')
    if original_order.status == 'cancelled':
        return error_response('原订单已取消，无法退货')

    # Build map of original order items: product_id -> purchased quantity
    order_items = {}
    for oi in original_order.items:
        order_items[oi.product_id] = order_items.get(oi.product_id, 0) + oi.quantity

    # Also consider already approved returns for this order
    existing_returns = db.session.query(
        SalesReturnItem.product_id,
        func.coalesce(func.sum(SalesReturnItem.quantity), 0).label('returned_qty')
    ).join(SalesReturn, SalesReturn.return_id == SalesReturnItem.return_id)\
     .filter(SalesReturn.original_order_id == data['original_order_id'],
             SalesReturn.status == 'completed')\
     .group_by(SalesReturnItem.product_id).all()
    returned_map = {r.product_id: r.returned_qty for r in existing_returns}

    for item in items_data:
        pid = item['product_id']
        qty = int(item['quantity'])
        purchased = order_items.get(pid, 0)
        already_returned = returned_map.get(pid, 0)
        if purchased == 0:
            return error_response(f'商品 {pid} 不在原订单中')
        if already_returned + qty > purchased:
            return error_response(f'商品 {pid} 退货数量 ({already_returned + qty}) 超过购买数量 ({purchased})')

    ret = SalesReturn(
        original_order_id=data['original_order_id'],
        member_id=data.get('member_id'),
        employee_id=data['employee_id'],
        return_amount=data.get('return_amount', 0),
        reason=data.get('reason', ''),
        status='pending'
    )
    db.session.add(ret)
    db.session.flush()

    total_refund = 0
    for item in items_data:
        total_refund += float(item.get('refund_amount', 0))
        ri = SalesReturnItem(
            return_id=ret.return_id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            refund_amount=item.get('refund_amount', 0)
        )
        db.session.add(ri)

    ret.return_amount = total_refund
    db.session.commit()
    log_operation('sales', 'create', 'SalesReturn', ret.return_id)
    return jsonify(success_response({'return_id': ret.return_id}, '退货申请已提交，等待审批'))


@bp.route('/api/sales-returns/<int:id>/approve', methods=['PUT'])
@require_auth
@require_permission('sales:crud')
def approve_return(id):
    ret = SalesReturn.query.get_or_404(id)
    if ret.status != 'pending':
        return error_response('只能审批待处理状态的退货单')
    ret.status = 'completed'

    original_order = SalesOrder.query.options(joinedload(SalesOrder.items)).get(ret.original_order_id)
    if not original_order:
        db.session.rollback()
        return error_response('原订单不存在')

    # Restore inventory on approval
    for item in ret.items:
        inv = Inventory.query.filter_by(product_id=item.product_id).first()
        if inv:
            inv.stock_quantity += item.quantity
        else:
            wh = Warehouse.query.first()
            if not wh:
                db.session.rollback()
                return error_response('无可用仓库')
            inv = Inventory(product_id=item.product_id, warehouse_id=wh.warehouse_id, stock_quantity=item.quantity)
            db.session.add(inv)

    # Check if all items in original order have been fully returned
    order_item_map = {}
    for oi in original_order.items:
        order_item_map[oi.product_id] = order_item_map.get(oi.product_id, 0) + oi.quantity

    all_returns = db.session.query(
        SalesReturnItem.product_id,
        func.coalesce(func.sum(SalesReturnItem.quantity), 0).label('total_returned')
    ).join(SalesReturn, SalesReturn.return_id == SalesReturnItem.return_id)\
     .filter(SalesReturn.original_order_id == ret.original_order_id,
             SalesReturn.status == 'completed')\
     .group_by(SalesReturnItem.product_id).all()
    returned_map = {r.product_id: r.total_returned for r in all_returns}

    fully_returned = all(
        returned_map.get(pid, 0) >= qty
        for pid, qty in order_item_map.items()
    )
    original_order.status = 'refunded' if fully_returned else 'completed'

    db.session.commit()
    log_operation('sales', 'approve', 'SalesReturn', id)
    return jsonify(success_response(message='退货审批成功，库存已恢复'))


# ==================== Sales Statistics & Rankings ====================

def build_sales_date_filter(period):
    today = date.today()
    if period == 'today':
        return func.date(SalesOrder.order_date) == today
    if period == 'month':
        month_start = today.replace(day=1)
        return func.date(SalesOrder.order_date) >= month_start
    return None


@bp.route('/api/sales-statistics', methods=['GET'])
@require_auth
def get_sales_statistics():
    period = request.args.get('period', '').strip()
    query = SalesOrder.query.filter(SalesOrder.status == 'completed')
    date_filter = build_sales_date_filter(period)
    if date_filter is not None:
        query = query.filter(date_filter)

    orders = query.all()
    order_ids = [o.order_id for o in orders]
    total_amount = sum(float(o.total_amount or 0) for o in orders)
    order_count = len(orders)

    product_count = 0
    if order_ids:
        product_count = db.session.query(func.count(func.distinct(SalesOrderItem.product_id)))\
            .filter(SalesOrderItem.order_id.in_(order_ids)).scalar() or 0

    period_label = {
        'today': '今日',
        'month': '本月'
    }.get(period, '全部')

    result = [{
        'stat_period': period_label,
        'total_amount': total_amount,
        'order_count': order_count,
        'product_count': product_count
    }]
    return jsonify(success_response(result))


@bp.route('/api/product-rankings', methods=['GET'])
@require_auth
def get_product_rankings():
    period = request.args.get('period', '').strip()
    query = db.session.query(
        SalesOrderItem.product_id,
        func.sum(SalesOrderItem.quantity).label('sales_quantity'),
        func.sum(SalesOrderItem.subtotal).label('sales_amount')
    ).join(SalesOrder, SalesOrder.order_id == SalesOrderItem.order_id)\
     .filter(SalesOrder.status == 'completed')

    date_filter = build_sales_date_filter(period)
    if date_filter is not None:
        query = query.filter(date_filter)

    rows = query.group_by(SalesOrderItem.product_id)\
        .order_by(func.sum(SalesOrderItem.subtotal).desc(), func.sum(SalesOrderItem.quantity).desc())\
        .limit(20).all()

    period_label = {
        'today': '今日',
        'month': '本月'
    }.get(period, '全部')

    result = []
    for index, row in enumerate(rows, start=1):
        product = Product.query.get(row.product_id)
        result.append({
            'rank_id': index,
            'product_id': row.product_id,
            'product_name': product.product_name if product else '未知商品',
            'sales_quantity': int(row.sales_quantity or 0),
            'sales_amount': float(row.sales_amount or 0),
            'rank_period': period_label,
            'rank_position': index
        })
    return jsonify(success_response(result))
