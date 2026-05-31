from flask import Blueprint, request, jsonify
from models import db
from models.purchase import PurchaseOrder, PurchaseOrderItem
from models.product import Product
from models.warehouse import Inventory, InboundRecord, InboundItem
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
import uuid

bp = Blueprint('purchases', __name__)


# ==================== Purchase Orders ====================

@bp.route('/api/purchase-orders', methods=['GET'])
@require_auth
def get_purchase_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    q = PurchaseOrder.query
    if status:
        q = q.filter(PurchaseOrder.status == status)
    if search:
        q = q.filter(PurchaseOrder.order_number.contains(search))

    total = q.count()
    rows = q.options(
        joinedload(PurchaseOrder.supplier),
        joinedload(PurchaseOrder.warehouse),
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.product)
    ).order_by(PurchaseOrder.order_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'order_id': r.order_id,
        'order_number': r.order_number,
        'supplier_id': r.supplier_id,
        'supplier_name': r.supplier.supplier_name if r.supplier else '',
        'contract_id': r.contract_id,
        'order_date': r.order_date.isoformat() if r.order_date else None,
        'total_amount': float(r.total_amount),
        'status': r.status,
        'delivery_date': r.delivery_date.isoformat() if r.delivery_date else None,
        'warehouse_id': r.warehouse_id,
        'warehouse_name': r.warehouse.warehouse_name if r.warehouse else '',
        'notes': r.notes,
        'payment_status': r.payment_status,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.product_name if item.product else '',
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'subtotal': float(item.subtotal)
        } for item in r.items]
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/purchase-orders', methods=['POST'])
@require_auth
@require_permission('purchase:crud')
def add_purchase_order():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'supplier_id')
    if missing: return error_response(f'缺少必填字段: {missing}')
    order = PurchaseOrder(
        supplier_id=data['supplier_id'],
        order_number=data.get('order_number', 'PO' + datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:4].upper()),
        order_date=datetime.strptime(data['order_date'], '%Y-%m-%d').date() if data.get('order_date') else datetime.now(timezone.utc).date(),
        total_amount=data.get('total_amount', 0),
        status=data.get('status') or 'draft',
        delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date() if data.get('delivery_date') else None,
        warehouse_id=data.get('warehouse_id'),
        created_by=get_current_employee_id(),
        contract_id=data.get('contract_id'),
        notes=data.get('notes', ''),
        payment_status=data.get('payment_status', 'unpaid')
    )
    db.session.add(order)
    db.session.flush()

    total = 0
    for item in data.get('items', []):
        pid = item.get('product_id')
        if not pid: continue
        subtotal = item['quantity'] * float(item['unit_price'])
        total += subtotal
        oi = PurchaseOrderItem(
            order_id=order.order_id,
            product_id=pid,
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            subtotal=subtotal
        )
        db.session.add(oi)

    order.total_amount = total
    db.session.commit()
    log_operation('purchase', 'create', 'PurchaseOrder', order.order_id, data.get('order_number', ''))
    return jsonify(success_response({'order_id': order.order_id}, '采购订单创建成功'))


@bp.route('/api/purchase-orders/<int:id>', methods=['PUT'])
@require_auth
@require_permission('purchase:crud')
def update_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['supplier_id', 'contract_id', 'delivery_date', 'warehouse_id', 'status', 'notes', 'payment_status']:
        if field in data:
            setattr(order, field, data[field])
    if 'order_date' in data:
        order.order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
    if 'items' in data:
        if order.status not in ('draft', 'pending'):
            return error_response('已审批或已完成的订单不可修改明细')
        PurchaseOrderItem.query.filter_by(order_id=id).delete()
        total = 0
        for item in data['items']:
            pid = item.get('product_id')
            if not pid: continue
            subtotal = item['quantity'] * float(item['unit_price'])
            total += subtotal
            oi = PurchaseOrderItem(
                order_id=id,
                product_id=pid,
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                subtotal=subtotal
            )
            db.session.add(oi)
        order.total_amount = total
    db.session.commit()
    log_operation('purchase', 'update', 'PurchaseOrder', id, data.get('order_number') or order.order_number)
    return jsonify(success_response(message='采购订单更新成功'))


@bp.route('/api/purchase-orders/<int:id>/approve', methods=['PUT'])
@require_auth
@require_permission('purchase:crud')
def approve_purchase_order(id):
    order = PurchaseOrder.query.get_or_404(id)
    if order.status not in ('draft', 'pending'):
        return error_response(f'当前状态 {order.status} 不可审批')
    order.status = 'approved'
    order.approved_by = get_current_employee_id()
    db.session.commit()
    log_operation('purchase', 'approve', 'PurchaseOrder', id, order.order_number)
    return jsonify(success_response(message='审批成功'))


@bp.route('/api/purchase-orders/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('purchase:crud')
def delete_purchase_order(id):
    try:
        PurchaseOrderItem.query.filter_by(order_id=id).delete()
        PurchaseOrder.query.filter_by(order_id=id).delete()
        db.session.commit()
        log_operation('purchase', 'delete', 'PurchaseOrder', id)
        return jsonify(success_response(message='采购订单删除成功'))
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除失败: 订单可能被其他记录引用')


# ==================== Inbound Records ====================

@bp.route('/api/inbound-records', methods=['GET'])
@require_auth
def get_inbound_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    q = InboundRecord.query
    if status:
        q = q.filter(InboundRecord.status == status)

    total = q.count()
    rows = q.options(
        joinedload(InboundRecord.supplier),
        joinedload(InboundRecord.warehouse),
        joinedload(InboundRecord.items).joinedload(InboundItem.product)
    ).order_by(InboundRecord.inbound_record_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'inbound_record_id': r.inbound_record_id,
        'inbound_no': r.inbound_no,
        'supplier_id': r.supplier_id,
        'supplier_name': r.supplier.supplier_name if r.supplier else '',
        'purchase_order_id': r.purchase_order_id,
        'warehouse_id': r.warehouse_id,
        'warehouse_name': r.warehouse.warehouse_name if r.warehouse else '',
        'total_quantity': r.total_quantity,
        'inbound_date': r.inbound_date.isoformat() if r.inbound_date else None,
        'status': r.status,
        'notes': r.notes,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.product_name if item.product else '',
            'batch_no': item.batch_no,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price) if item.unit_price else None,
            'bin_location': item.bin_location
        } for item in r.items]
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/inbound-records', methods=['POST'])
@require_auth
@require_permission('purchase:crud')
def add_inbound_record():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'supplier_id', 'warehouse_id')
    if missing: return error_response(f'缺少必填字段: {missing}')
    purchase_order_id = data.get('purchase_order_id')
    if purchase_order_id is not None:
        try: purchase_order_id = int(purchase_order_id)
        except: purchase_order_id = None
    record = InboundRecord(
        inbound_no=data.get('inbound_no', 'IN' + datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:4].upper()),
        supplier_id=data['supplier_id'],
        warehouse_id=data['warehouse_id'],
        purchase_order_id=purchase_order_id,
        total_quantity=data.get('total_quantity', 0),
        inbound_date=datetime.fromisoformat(data['inbound_date']) if data.get('inbound_date') else datetime.now(timezone.utc),
        status=data.get('status') or 'pending',
        created_by=get_current_employee_id(),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.flush()

    total_qty = 0
    for item in data.get('items', []):
        pid = item.get('product_id')
        if not pid: continue
        qty = item.get('quantity', 0)
        total_qty += qty
        ii = InboundItem(
            inbound_record_id=record.inbound_record_id,
            product_id=pid,
            batch_no=item.get('batch_no', ''),
            quantity=qty,
            unit_price=item.get('unit_price'),
            expiry_date=datetime.strptime(item['expiry_date'], '%Y-%m-%d').date() if item.get('expiry_date') else None,
            bin_location=item.get('bin_location', '')
        )
        db.session.add(ii)

        inv = Inventory.query.filter_by(product_id=pid, warehouse_id=data['warehouse_id']).first()
        if inv:
            inv.stock_quantity += qty
            inv.last_restock_date = datetime.now(timezone.utc)
        else:
            inv = Inventory(
                product_id=pid,
                warehouse_id=data['warehouse_id'],
                stock_quantity=qty
            )
            db.session.add(inv)
        if item.get('unit_price'):
            product = Product.query.get(pid)
            if product:
                product.cost_price = item['unit_price']

    record.total_quantity = total_qty
    try:
        db.session.commit()
        log_operation('purchase', 'create', 'InboundRecord', record.inbound_record_id, data.get('inbound_no', ''))
        return jsonify(success_response({'inbound_record_id': record.inbound_record_id}, '入库记录创建成功'))
    except Exception as e:
        db.session.rollback()
        return error_response(f'入库失败: {str(e)}')


@bp.route('/api/inbound-records/<int:id>', methods=['PUT'])
@require_auth
@require_permission('purchase:crud')
def update_inbound_record(id):
    record = InboundRecord.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['supplier_id', 'warehouse_id', 'purchase_order_id', 'status', 'notes']:
        if field in data:
            setattr(record, field, data[field])
    if data.get('inbound_date'):
        record.inbound_date = datetime.fromisoformat(data['inbound_date'])
    if 'items' in data:
        InboundItem.query.filter_by(inbound_record_id=id).delete()
        total_qty = 0
        for item in data['items']:
            pid = item.get('product_id')
            if not pid: continue
            qty = item.get('quantity', 0)
            total_qty += qty
            ii = InboundItem(
                inbound_record_id=id,
                product_id=pid,
                batch_no=item.get('batch_no', ''),
                quantity=qty,
                unit_price=item.get('unit_price'),
                bin_location=item.get('bin_location', '')
            )
            db.session.add(ii)
        record.total_quantity = total_qty
    db.session.commit()
    log_operation('purchase', 'update', 'InboundRecord', id, data.get('inbound_no') or record.inbound_no)
    return jsonify(success_response(message='入库记录更新成功'))


@bp.route('/api/inbound-records/<int:id>/receive', methods=['PUT'])
@require_auth
@require_permission('purchase:crud')
def receive_inbound_record(id):
    record = InboundRecord.query.get_or_404(id)
    if record.status != 'pending':
        return error_response('只能确认收货待处理状态的入库记录')
    record.status = 'received'
    db.session.commit()
    log_operation('purchase', 'receive', 'InboundRecord', id, record.inbound_no)
    return jsonify(success_response(message='确认收货成功'))


@bp.route('/api/inbound-records/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('purchase:crud')
def delete_inbound_record(id):
    try:
        InboundItem.query.filter_by(inbound_record_id=id).delete()
        InboundRecord.query.filter_by(inbound_record_id=id).delete()
        db.session.commit()
        log_operation('purchase', 'delete', 'InboundRecord', id)
        return jsonify(success_response(message='入库记录删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，入库记录可能存在关联数据')
