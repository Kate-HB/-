from flask import Blueprint, request, jsonify
from models import db
from models.warehouse import Warehouse, Inventory, InventoryDetail, OutboundRecord, OutboundItem
from models.product import Product
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime, timezone
import uuid

bp = Blueprint('warehouses', __name__)


# ==================== Warehouses ====================

@bp.route('/api/warehouses', methods=['GET'])
@require_auth
def get_warehouses():
    rows = Warehouse.query.all()
    result = [{
        'warehouse_id': r.warehouse_id,
        'warehouse_name': r.warehouse_name,
        'location': r.location,
        'capacity': r.capacity,
        'status': r.status
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/warehouses', methods=['POST'])
@require_auth
@require_permission('warehouse:crud')
def add_warehouse():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'warehouse_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    wh = Warehouse(
        warehouse_name=data['warehouse_name'],
        location=data.get('location', ''),
        capacity=data.get('capacity'),
        status=data.get('status', 'active')
    )
    db.session.add(wh)
    db.session.commit()
    log_operation('warehouse', 'create', 'Warehouse', wh.warehouse_id, data.get('warehouse_name', ''))
    return jsonify(success_response({'warehouse_id': wh.warehouse_id}, '仓库添加成功'))


@bp.route('/api/warehouses/<int:id>', methods=['PUT'])
@require_auth
@require_permission('warehouse:crud')
def update_warehouse(id):
    wh = Warehouse.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['warehouse_name', 'location', 'capacity', 'status']:
        if field in data:
            setattr(wh, field, data[field])
    db.session.commit()
    log_operation('warehouse', 'update', 'Warehouse', id, data.get('warehouse_name') or wh.warehouse_name)
    return jsonify(success_response(message='仓库更新成功'))


# ==================== Inventory ====================

@bp.route('/api/inventory', methods=['GET'])
@require_auth
def get_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    q = Inventory.query
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    if status:
        status_values = [item.strip() for item in status.split(',') if item.strip()]
        if len(status_values) > 1:
            q = q.filter(Inventory.status.in_(status_values))
        else:
            q = q.filter(Inventory.status == status_values[0])
    if search:
        q = q.join(Product).filter(Product.product_name.contains(search))

    total = q.count()
    rows = q.order_by(Inventory.inventory_id).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'inventory_id': r.inventory_id,
        'product_id': r.product_id,
        'product_name': r.product.product_name,
        'warehouse_id': r.warehouse_id,
        'warehouse_name': r.warehouse.warehouse_name,
        'stock_quantity': r.stock_quantity,
        'safety_stock': r.safety_stock,
        'last_restock_date': r.last_restock_date.isoformat() if r.last_restock_date else None,
        'status': r.status
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/inventory/adjust', methods=['POST'])
@require_auth
@require_permission('warehouse:crud')
def adjust_inventory():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'inventory_id', 'stock_quantity')
    if missing: return error_response(f'缺少必填字段: {missing}')
    inv = Inventory.query.get_or_404(data['inventory_id'])
    if int(data['stock_quantity']) < 0:
        return error_response('库存数量不能为负数')
    inv.stock_quantity = data['stock_quantity']
    if inv.stock_quantity <= 0:
        inv.status = 'out_of_stock'
    elif inv.stock_quantity <= inv.safety_stock:
        inv.status = 'low'
    else:
        inv.status = 'normal'
    db.session.commit()
    log_operation('warehouse', 'adjust')
    return jsonify(success_response(message='库存调整成功'))


# ==================== Inventory Details ====================

@bp.route('/api/inventory-details', methods=['GET'])
@require_auth
def get_inventory_details():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    warehouse_id = request.args.get('warehouse_id', type=int)

    q = InventoryDetail.query
    if warehouse_id:
        q = q.filter(InventoryDetail.warehouse_id == warehouse_id)

    total = q.count()
    rows = q.order_by(InventoryDetail.inventory_detail_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'inventory_detail_id': r.inventory_detail_id,
        'warehouse_id': r.warehouse_id,
        'warehouse_name': r.warehouse.warehouse_name,
        'product_id': r.product_id,
        'product_name': r.product.product_name,
        'batch_no': r.batch_no,
        'quantity': r.quantity,
        'bin_location': r.bin_location,
        'expiry_date': r.expiry_date.isoformat() if r.expiry_date else None,
        'status': r.status
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


# ==================== Outbound Records ====================

@bp.route('/api/outbound-records', methods=['GET'])
@require_auth
def get_outbound_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    q = OutboundRecord.query
    if status:
        q = q.filter(OutboundRecord.status == status)

    total = q.count()
    rows = q.order_by(OutboundRecord.outbound_record_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'outbound_record_id': r.outbound_record_id,
        'outbound_no': r.outbound_no,
        'source_order_id': r.source_order_id,
        'warehouse_id': r.warehouse_id,
        'warehouse_name': r.warehouse.warehouse_name,
        'total_quantity': r.total_quantity,
        'outbound_date': r.outbound_date.isoformat() if r.outbound_date else None,
        'status': r.status,
        'notes': r.notes,
        'items': [{
            'product_id': item.product_id,
            'product_name': item.product.product_name,
            'batch_no': item.batch_no,
            'quantity': item.quantity,
            'bin_location': item.bin_location
        } for item in r.items]
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/outbound-records', methods=['POST'])
@require_auth
@require_permission('warehouse:crud')
def add_outbound_record():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'warehouse_id')
    if missing: return error_response(f'缺少必填字段: {missing}')
    record = OutboundRecord(
        outbound_no=data.get('outbound_no', 'OUT' + datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:4].upper()),
        source_order_id=data.get('source_order_id'),
        warehouse_id=data['warehouse_id'],
        total_quantity=data.get('total_quantity', 0),
        outbound_date=datetime.fromisoformat(data['outbound_date']) if data.get('outbound_date') else datetime.now(timezone.utc),
        status=data.get('status', 'pending'),
        created_by=get_current_employee_id(),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.flush()

    total_qty = 0
    for item in data.get('items', []):
        total_qty += item['quantity']
        oi = OutboundItem(
            outbound_record_id=record.outbound_record_id,
            product_id=item['product_id'],
            batch_no=item.get('batch_no', ''),
            quantity=item['quantity'],
            bin_location=item.get('bin_location', '')
        )
        db.session.add(oi)

        inv = Inventory.query.filter_by(product_id=item['product_id'], warehouse_id=data['warehouse_id']).first()
        if inv:
            if inv.stock_quantity < item['quantity']:
                db.session.rollback()
                return error_response(f'商品 {item["product_id"]} 库存不足')
            inv.stock_quantity -= item['quantity']

    record.total_quantity = total_qty
    db.session.commit()
    log_operation('warehouse', 'create', 'OutboundRecord', record.outbound_record_id, data.get('outbound_no', ''))
    return jsonify(success_response({'outbound_record_id': record.outbound_record_id}, '出库记录创建成功'))


@bp.route('/api/outbound-records/<int:id>', methods=['PUT'])
@require_auth
@require_permission('warehouse:crud')
def update_outbound_record(id):
    record = OutboundRecord.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['warehouse_id', 'status', 'notes']:
        if field in data:
            setattr(record, field, data[field])
    if data.get('outbound_date'):
        record.outbound_date = datetime.fromisoformat(data['outbound_date'])
    db.session.commit()
    log_operation('warehouse', 'update', 'OutboundRecord', id, data.get('outbound_no') or record.outbound_no)
    return jsonify(success_response(message='出库记录更新成功'))


@bp.route('/api/outbound-records/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('warehouse:crud')
def delete_outbound_record(id):
    try:
        OutboundItem.query.filter_by(outbound_record_id=id).delete()
        OutboundRecord.query.filter_by(outbound_record_id=id).delete()
        db.session.commit()
        log_operation('warehouse', 'delete', 'OutboundRecord', id)
        return jsonify(success_response(message='出库记录删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，出库记录可能存在关联数据')
