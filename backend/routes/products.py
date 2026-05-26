from flask import Blueprint, request, jsonify
from models import db
from models.product import Category, Product, Promotion, PromotionProduct
from models.supplier import Supplier
from models.warehouse import Inventory, Warehouse
from models.sales import SalesOrderItem
from models.purchase import PurchaseOrderItem
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission
from utils.operation_log import log_operation
from sqlalchemy import func
from datetime import datetime

bp = Blueprint('products', __name__)


def sync_inventory_status(inventory):
    if inventory.stock_quantity <= 0:
        inventory.status = 'out_of_stock'
    elif inventory.stock_quantity <= inventory.safety_stock:
        inventory.status = 'low'
    else:
        inventory.status = 'normal'


# ==================== Products ====================

@bp.route('/api/products', methods=['GET'])
@require_auth
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', '')

    base = db.session.query(Product).join(Category, Product.category_id == Category.category_id)\
        .join(Supplier, Product.supplier_id == Supplier.supplier_id)
    if search:
        base = base.filter(Product.product_name.contains(search))
    if category_id:
        base = base.filter(Product.category_id == category_id)
    if status:
        base = base.filter(Product.status == status)

    total = base.count()
    q = base.with_entities(
        Product, Category.category_name, Supplier.supplier_name,
        func.coalesce(func.sum(Inventory.stock_quantity), 0).label('total_stock')
    ).outerjoin(Inventory, Product.product_id == Inventory.product_id)\
     .group_by(Product.product_id, Category.category_name, Supplier.supplier_name)
    rows = q.offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'product_id': r[0].product_id,
        'product_name': r[0].product_name,
        'description': r[0].description,
        'category_id': r[0].category_id,
        'category_name': r[1],
        'supplier_id': r[0].supplier_id,
        'supplier_name': r[2],
        'base_price': float(r[0].base_price),
        'cost_price': float(r[0].cost_price) if r[0].cost_price else None,
        'barcode': r[0].barcode,
        'spec': r[0].spec,
        'unit': r[0].unit,
        'status': r[0].status,
        'stock_quantity': int(r[3]),
        'created_at': r[0].created_at.isoformat() if r[0].created_at else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/products', methods=['POST'])
@require_auth
@require_permission('product:crud')
def add_product():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'product_name', 'category_id', 'supplier_id', 'base_price')
    if missing: return error_response(f'缺少必要字段: {missing}')
    if float(data['base_price']) <= 0:
        return error_response('商品价格必须大于0')
    product = Product(
        product_name=data['product_name'],
        description=data.get('description', ''),
        category_id=data['category_id'],
        supplier_id=data['supplier_id'],
        base_price=data['base_price'],
        cost_price=data.get('cost_price'),
        barcode=data.get('barcode', ''),
        spec=data.get('spec', ''),
        unit=data.get('unit', ''),
        status=data.get('status', 'active')
    )
    db.session.add(product)
    db.session.flush()

    stock_quantity = max(int(data.get('stock_quantity', 0)), 0)
    safety_stock = max(int(data.get('safety_stock') or 10), 0)
    warehouse_id = data.get('warehouse_id')
    if warehouse_id:
        inv = Inventory(
            product_id=product.product_id,
            warehouse_id=warehouse_id,
            stock_quantity=stock_quantity,
            safety_stock=safety_stock
        )
        sync_inventory_status(inv)
        db.session.add(inv)
    else:
        warehouses = Warehouse.query.all()
        if warehouses:
            for index, wh in enumerate(warehouses):
                inv = Inventory(
                    product_id=product.product_id,
                    warehouse_id=wh.warehouse_id,
                    stock_quantity=stock_quantity if index == 0 else 0,
                    safety_stock=safety_stock
                )
                sync_inventory_status(inv)
                db.session.add(inv)

    db.session.commit()
    log_operation('product', 'create', 'Product', product.product_id, data.get('product_name', ''))
    return jsonify(success_response({'product_id': product.product_id}, '商品添加成功'))


@bp.route('/api/products/<int:id>', methods=['PUT'])
@require_auth
@require_permission('product:crud')
def update_product(id):
    product = Product.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['product_name', 'description', 'category_id', 'supplier_id',
                  'base_price', 'cost_price', 'barcode', 'spec', 'unit', 'status']:
        if field in data:
            setattr(product, field, data[field])
    if 'stock_quantity' in data:
        stock_quantity = max(int(data['stock_quantity'] or 0), 0)
        inventories = Inventory.query.filter_by(product_id=id).order_by(Inventory.inventory_id.asc()).all()
        if inventories:
            first = inventories[0]
            first.stock_quantity = stock_quantity
            sync_inventory_status(first)
            for inv in inventories[1:]:
                if inv.stock_quantity < 0:
                    inv.stock_quantity = 0
                sync_inventory_status(inv)
        elif data.get('warehouse_id'):
            inv = Inventory(
                product_id=id,
                warehouse_id=data['warehouse_id'],
                stock_quantity=stock_quantity,
                safety_stock=max(int(data.get('safety_stock') or 10), 0)
            )
            sync_inventory_status(inv)
            db.session.add(inv)
    db.session.commit()
    log_operation('product', 'update', 'Product', id, data.get('product_name') or product.product_name)
    return jsonify(success_response(message='商品更新成功'))


@bp.route('/api/products/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('product:crud')
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        SalesOrderItem.query.filter_by(product_id=id).delete()
        PurchaseOrderItem.query.filter_by(product_id=id).delete()
        PromotionProduct.query.filter_by(product_id=id).delete()
        Inventory.query.filter_by(product_id=id).delete()
        Product.query.filter_by(product_id=id).delete()
        db.session.commit()
        log_operation('product', 'delete', 'Product', id, product.product_name)
        return jsonify(success_response(message='商品删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，商品可能存在关联数据')


# ==================== Categories ====================

@bp.route('/api/categories', methods=['GET'])
@require_auth
def get_categories():
    rows = Category.query.order_by(Category.sort_order).all()
    result = [{
        'category_id': r.category_id,
        'category_name': r.category_name,
        'parent_category_id': r.parent_category_id,
        'description': r.description,
        'sort_order': r.sort_order
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/categories', methods=['POST'])
@require_auth
@require_permission('product:crud')
def add_category():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'category_name')
    if missing: return error_response(f'缺少必要字段: {missing}')
    cat = Category(
        category_name=data['category_name'],
        parent_category_id=data.get('parent_category_id'),
        description=data.get('description', ''),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(cat)
    db.session.commit()
    log_operation('product', 'create', 'Category', cat.category_id, data.get('category_name', ''))
    return jsonify(success_response({'category_id': cat.category_id}, '分类添加成功'))


@bp.route('/api/categories/<int:id>', methods=['PUT'])
@require_auth
@require_permission('product:crud')
def update_category(id):
    cat = Category.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['category_name', 'parent_category_id', 'description', 'sort_order']:
        if field in data:
            if field == 'parent_category_id' and data[field] == id:
                return error_response('不能将自己设为父分类')
            setattr(cat, field, data[field])
    db.session.commit()
    log_operation('product', 'update', 'Category', id, data.get('category_name') or cat.category_name)
    return jsonify(success_response(message='分类更新成功'))


@bp.route('/api/categories/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('product:crud')
def delete_category(id):
    if Category.query.filter_by(parent_category_id=id).first():
        return error_response('该分类下有子分类，请先删除子分类')
    if Product.query.filter_by(category_id=id).first():
        return error_response('该分类下有商品，无法删除')
    try:
        Category.query.filter_by(category_id=id).delete()
        db.session.commit()
        log_operation('product', 'delete', 'Category', id)
        return jsonify(success_response(message='分类删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，分类可能存在关联数据')


# ==================== Promotions ====================

@bp.route('/api/promotions', methods=['GET'])
@require_auth
def get_promotions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    q = Promotion.query
    if status:
        q = q.filter(Promotion.status == status)
    total = q.count()
    rows = q.order_by(Promotion.promotion_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    product_ids = set()
    for r in rows:
        for pp in r.promotion_products:
            product_ids.add(pp.product_id)
    product_map = {}
    if product_ids:
        products = Product.query.filter(Product.product_id.in_(product_ids)).all()
        product_map = {p.product_id: p for p in products}

    result = []
    for r in rows:
        promo = {
            'promotion_id': r.promotion_id,
            'promotion_name': r.promotion_name,
            'promotion_type': r.promotion_type,
            'discount_rate': float(r.discount_rate) if r.discount_rate else None,
            'fixed_amount': float(r.fixed_amount) if r.fixed_amount else None,
            'min_amount': float(r.min_amount) if r.min_amount else None,
            'min_quantity': r.min_quantity,
            'gift_quantity': r.gift_quantity or 1,
            'gift_product_id': r.gift_product_id,
            'gift_product_name': r.gift_product.product_name if r.gift_product else None,
            'start_date': r.start_date.isoformat() if r.start_date else None,
            'end_date': r.end_date.isoformat() if r.end_date else None,
            'status': r.status,
            'products': []
        }
        for pp in r.promotion_products:
            p = product_map.get(pp.product_id)
            promo['products'].append({
                'product_id': pp.product_id,
                'product_name': p.product_name if p else '',
                'specific_discount': float(pp.specific_discount) if pp.specific_discount else None
            })
        result.append(promo)

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/promotions', methods=['POST'])
@require_auth
@require_permission('product:crud')
def add_promotion():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'promotion_name', 'promotion_type', 'start_date', 'end_date')
    if missing: return error_response(f'缺少必要字段: {missing}')
    if 'start_date' in data and 'end_date' in data and data['start_date'] and data['end_date']:
        if data['end_date'] <= data['start_date']:
            return error_response('结束日期必须晚于开始日期')
    if 'discount_rate' in data and data['discount_rate'] is not None:
        dr = float(data['discount_rate'])
        if dr < 0 or dr > 1:
            return error_response('折扣率必须在0-1之间')
    promo = Promotion(
        promotion_name=data['promotion_name'],
        promotion_type=data['promotion_type'],
        discount_rate=data.get('discount_rate'),
        fixed_amount=data.get('fixed_amount'),
        min_amount=data.get('min_amount'),
        min_quantity=data.get('min_quantity'),
        gift_quantity=data.get('gift_quantity', 1),
        gift_product_id=data.get('gift_product_id'),
        start_date=datetime.fromisoformat(data['start_date']),
        end_date=datetime.fromisoformat(data['end_date']),
        status=data.get('status', 'pending')
    )
    db.session.add(promo)
    db.session.flush()

    for p in data.get('products', []):
        pp = PromotionProduct(
            promotion_id=promo.promotion_id,
            product_id=p['product_id'],
            specific_discount=p.get('specific_discount')
        )
        db.session.add(pp)

    db.session.commit()
    log_operation('product', 'create', 'Promotion', promo.promotion_id, data.get('promotion_name', ''))
    return jsonify(success_response({'promotion_id': promo.promotion_id}, '促销添加成功'))


@bp.route('/api/promotions/<int:id>', methods=['PUT'])
@require_auth
@require_permission('product:crud')
def update_promotion(id):
    promo = Promotion.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['promotion_name', 'promotion_type', 'discount_rate', 'fixed_amount', 'min_amount', 'min_quantity', 'gift_quantity', 'gift_product_id', 'status']:
        if field in data:
            setattr(promo, field, data[field])
    if 'discount_rate' in data and data['discount_rate'] is not None:
        dr = float(data['discount_rate'])
        if dr < 0 or dr > 1:
            return error_response('折扣率必须在0-1之间')
    if 'start_date' in data and data['start_date']:
        promo.start_date = datetime.fromisoformat(data['start_date'])
    if 'end_date' in data and data['end_date']:
        promo.end_date = datetime.fromisoformat(data['end_date'])
    if promo.start_date and promo.end_date and promo.end_date <= promo.start_date:
        return error_response('结束日期必须晚于开始日期')
    if 'products' in data:
        PromotionProduct.query.filter_by(promotion_id=id).delete()
        for p in data['products']:
            pp = PromotionProduct(
                promotion_id=id,
                product_id=p['product_id'],
                specific_discount=p.get('specific_discount')
            )
            db.session.add(pp)
    db.session.commit()
    log_operation('product', 'update', 'Promotion', id, data.get('promotion_name') or promo.promotion_name)
    return jsonify(success_response(message='促销更新成功'))


@bp.route('/api/promotions/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('product:crud')
def delete_promotion(id):
    promo = Promotion.query.get_or_404(id)
    try:
        PromotionProduct.query.filter_by(promotion_id=id).delete()
        Promotion.query.filter_by(promotion_id=id).delete()
        db.session.commit()
        log_operation('product', 'delete', 'Promotion', id, promo.promotion_name)
        return jsonify(success_response(message='促销删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，促销可能存在关联数据')
