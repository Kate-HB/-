from flask import Blueprint, request, jsonify
from models import db
from models.supplier import Supplier, SupplierContract, SupplierEvaluation
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime

bp = Blueprint('suppliers', __name__)


# ==================== Suppliers ====================

@bp.route('/api/suppliers', methods=['GET'])
@require_auth
def get_suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')

    q = Supplier.query
    if search:
        q = q.filter(Supplier.supplier_name.contains(search))

    total = q.count()
    rows = q.order_by(Supplier.supplier_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'supplier_id': r.supplier_id,
        'supplier_name': r.supplier_name,
        'contact_person': r.contact_person,
        'phone': r.phone,
        'address': r.address,
        'credit_level': r.credit_level,
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/suppliers', methods=['POST'])
@require_auth
@require_permission('supplier:crud')
def add_supplier():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'supplier_name')
    if missing: return error_response(f'缺少必要字段: {missing}')
    supplier = Supplier(
        supplier_name=data['supplier_name'],
        contact_person=data.get('contact_person', ''),
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        credit_level=data.get('credit_level', '')
    )
    db.session.add(supplier)
    db.session.commit()
    log_operation('supplier', 'create', 'Supplier', supplier.supplier_id, data.get('supplier_name', ''))
    return jsonify(success_response({'supplier_id': supplier.supplier_id}, '供应商添加成功'))


@bp.route('/api/suppliers/<int:id>', methods=['PUT'])
@require_auth
@require_permission('supplier:crud')
def update_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['supplier_name', 'contact_person', 'phone', 'address', 'credit_level']:
        if field in data:
            setattr(supplier, field, data[field])
    db.session.commit()
    log_operation('supplier', 'update', 'Supplier', id, data.get('supplier_name') or supplier.supplier_name)
    return jsonify(success_response(message='供应商更新成功'))


@bp.route('/api/suppliers/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('supplier:crud')
def delete_supplier(id):
    try:
        Supplier.query.filter_by(supplier_id=id).delete()
        db.session.commit()
        log_operation('supplier', 'delete', 'Supplier', id)
        return jsonify(success_response(message='供应商删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，供应商可能存在关联数据')


# ==================== Supplier Contracts ====================

@bp.route('/api/supplier-contracts', methods=['GET'])
@require_auth
def get_contracts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    q = SupplierContract.query
    if status:
        q = q.filter(SupplierContract.status == status)

    total = q.count()
    rows = q.order_by(SupplierContract.contract_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'contract_id': r.contract_id,
        'supplier_id': r.supplier_id,
        'supplier_name': r.supplier.supplier_name,
        'contract_number': r.contract_number,
        'contract_type': r.contract_type,
        'start_date': r.start_date.isoformat() if r.start_date else None,
        'end_date': r.end_date.isoformat() if r.end_date else None,
        'total_amount': float(r.total_amount) if r.total_amount else None,
        'status': r.status,
        'signed_date': r.signed_date.isoformat() if r.signed_date else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/supplier-contracts', methods=['POST'])
@require_auth
@require_permission('supplier:crud')
def add_contract():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'supplier_id', 'contract_number', 'start_date', 'end_date')
    if missing: return error_response(f'缺少必要字段: {missing}')
    def parse_date(val):
        if not val: return None
        try:
            return datetime.strptime(val, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    contract = SupplierContract(
        supplier_id=data['supplier_id'],
        contract_number=data['contract_number'],
        contract_type=data.get('contract_type', ''),
        start_date=parse_date(data.get('start_date')),
        end_date=parse_date(data.get('end_date')),
        total_amount=data.get('total_amount', 0),
        status=data.get('status', 'pending'),
        signed_date=parse_date(data.get('signed_date'))
    )
    db.session.add(contract)
    db.session.commit()
    log_operation('supplier', 'create', 'SupplierContract', contract.contract_id, data.get('contract_number', ''))
    return jsonify(success_response({'contract_id': contract.contract_id}, '合同添加成功'))


@bp.route('/api/supplier-contracts/<int:id>', methods=['PUT'])
@require_auth
@require_permission('supplier:crud')
def update_contract(id):
    contract = SupplierContract.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['supplier_id', 'contract_number', 'contract_type', 'total_amount', 'status']:
        if field in data:
            setattr(contract, field, data[field])
    for date_field in ['start_date', 'end_date', 'signed_date']:
        if date_field in data and data[date_field]:
            try:
                setattr(contract, date_field, datetime.strptime(data[date_field], '%Y-%m-%d').date())
            except (ValueError, TypeError):
                pass
    db.session.commit()
    log_operation('supplier', 'update', 'SupplierContract', id, data.get('contract_number') or contract.contract_number)
    return jsonify(success_response(message='合同更新成功'))


@bp.route('/api/supplier-contracts/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('supplier:crud')
def delete_contract(id):
    try:
        SupplierContract.query.filter_by(contract_id=id).delete()
        db.session.commit()
        log_operation('supplier', 'delete', 'SupplierContract', id)
        return jsonify(success_response(message='合同删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，合同可能存在关联数据')


# ==================== Supplier Evaluations ====================

@bp.route('/api/supplier-evaluations', methods=['GET'])
@require_auth
def get_evaluations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    q = SupplierEvaluation.query
    total = q.count()
    rows = q.order_by(SupplierEvaluation.evaluation_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'evaluation_id': r.evaluation_id,
        'supplier_id': r.supplier_id,
        'supplier_name': r.supplier.supplier_name,
        'evaluator_id': r.evaluator_id,
        'evaluator_name': r.evaluator.employee_name if r.evaluator else '',
        'score': float(r.score),
        'quality_score': float(r.quality_score) if r.quality_score else None,
        'delivery_score': float(r.delivery_score) if r.delivery_score else None,
        'service_score': float(r.service_score) if r.service_score else None,
        'evaluation_date': r.evaluation_date.isoformat() if r.evaluation_date else None,
        'comments': r.comments
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/supplier-evaluations', methods=['POST'])
@require_auth
@require_permission('supplier:crud')
def add_evaluation():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'supplier_id', 'score')
    if missing: return error_response(f'缺少必要字段: {missing}')
    def parse_date(val):
        if not val: return None
        try:
            return datetime.strptime(val, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    ev = SupplierEvaluation(
        supplier_id=data['supplier_id'],
        evaluator_id=data.get('evaluator_id') or get_current_employee_id(),
        score=data['score'],
        quality_score=data.get('quality_score'),
        delivery_score=data.get('delivery_score'),
        service_score=data.get('service_score'),
        evaluation_date=parse_date(data.get('evaluation_date')),
        comments=data.get('comments', '')
    )
    db.session.add(ev)
    db.session.commit()
    log_operation('supplier', 'create', 'SupplierEvaluation', ev.evaluation_id)
    return jsonify(success_response({'evaluation_id': ev.evaluation_id}, '评价添加成功'))
