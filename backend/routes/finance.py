from flask import Blueprint, request, jsonify
from models import db
from models.finance import CashRecord, Account, JournalEntry, JournalEntryItem, Budget, TaxDeclaration
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy import func
import uuid

bp = Blueprint('finance', __name__)


# ==================== Cash Records ====================

@bp.route('/api/cash-records', methods=['GET'])
@require_auth
def get_cash_records():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    payment_method = request.args.get('payment_method', '')

    q = CashRecord.query
    if payment_method:
        q = q.filter(CashRecord.payment_method == payment_method)

    total = q.count()
    rows = q.order_by(CashRecord.cash_record_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'cash_record_id': r.cash_record_id,
        'order_id': r.order_id,
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'amount': float(r.amount),
        'payment_method': r.payment_method,
        'transaction_time': r.transaction_time.isoformat() if r.transaction_time else None,
        'status': r.status
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/cash-records', methods=['POST'])
@require_auth
@require_permission('finance:crud')
def add_cash_record():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_id', 'amount', 'payment_method', 'order_id')
    if missing: return error_response(f'缺少必填字段: {missing}')
    cr = CashRecord(
        order_id=data.get('order_id'),
        employee_id=data['employee_id'],
        amount=data['amount'],
        payment_method=data['payment_method'],
        transaction_time=datetime.fromisoformat(data['transaction_time']) if data.get('transaction_time') else datetime.now(timezone.utc),
        status=data.get('status', 'completed')
    )
    db.session.add(cr)
    db.session.commit()
    log_operation('finance', 'create', 'CashRecord', cr.cash_record_id)
    return jsonify(success_response({'cash_record_id': cr.cash_record_id}, '收银记录创建成功'))


# ==================== Accounts ====================

@bp.route('/api/accounts', methods=['GET'])
@require_auth
def get_accounts():
    rows = Account.query.all()
    result = [{
        'account_id': r.account_id,
        'account_code': r.account_code,
        'account_name': r.account_name,
        'account_type': r.account_type,
        'parent_id': r.parent_id,
        'balance': float(r.balance)
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/accounts', methods=['POST'])
@require_auth
@require_permission('finance:crud')
def add_account():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'account_code', 'account_name', 'account_type')
    if missing: return error_response(f'缺少必填字段: {missing}')
    acc = Account(
        account_code=data['account_code'],
        account_name=data['account_name'],
        account_type=data['account_type'],
        parent_id=data.get('parent_id'),
        balance=data.get('balance', 0)
    )
    db.session.add(acc)
    db.session.commit()
    log_operation('finance', 'create', 'Account', acc.account_id, data.get('account_name', ''))
    return jsonify(success_response({'account_id': acc.account_id}, '科目添加成功'))


@bp.route('/api/accounts/<int:id>', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def update_account(id):
    acc = Account.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['account_code', 'account_name', 'account_type', 'parent_id', 'balance']:
        if field in data:
            setattr(acc, field, data[field])
    db.session.commit()
    log_operation('finance', 'update', 'Account', id, data.get('account_name') or acc.account_name)
    return jsonify(success_response(message='科目更新成功'))


# ==================== Journal Entries ====================

@bp.route('/api/journal-entries', methods=['GET'])
@require_auth
def get_journal_entries():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status', '')

    q = JournalEntry.query.options(
        joinedload(JournalEntry.items).joinedload(JournalEntryItem.account)
    )
    if status:
        q = q.filter(JournalEntry.status == status)

    total = q.count()
    rows = q.order_by(JournalEntry.journal_entry_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'journal_entry_id': r.journal_entry_id,
        'voucher_no': r.voucher_no,
        'entry_date': r.entry_date.isoformat() if r.entry_date else None,
        'description': r.description,
        'total_debit': float(r.total_debit),
        'total_credit': float(r.total_credit),
        'status': r.status,
        'items': [{
            'item_id': item.item_id,
            'account_id': item.account_id,
            'account_name': item.account.account_name if item.account else '',
            'debit_amount': float(item.debit_amount),
            'credit_amount': float(item.credit_amount),
            'description': item.description
        } for item in r.items]
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/journal-entries', methods=['POST'])
@require_auth
@require_permission('finance:crud')
def add_journal_entry():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'entry_date', 'description')
    if missing: return error_response(f'缺少必填字段: {missing}')
    items = data.get('items', [])
    if not items:
        return error_response('分录明细不能为空')
    total_debit = 0
    total_credit = 0
    for item in items:
        d = float(item.get('debit_amount', 0) or 0)
        c = float(item.get('credit_amount', 0) or 0)
        if d == 0 and c == 0:
            return error_response('每行分录必须填写借方或贷方金额')
        if d > 0 and c > 0:
            return error_response('每行分录不能同时填写借方和贷方金额')
        total_debit += d
        total_credit += c

    if abs(total_debit - total_credit) > 0.01:
        return error_response('借贷不平衡，借方合计必须等于贷方合计')

    def parse_date(val):
        if not val: return datetime.now(timezone.utc).date()
        try:
            return datetime.strptime(val, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return datetime.now(timezone.utc).date()

    entry = JournalEntry(
        voucher_no=data.get('voucher_no', 'JV' + datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:4].upper()),
        entry_date=parse_date(data.get('entry_date')),
        description=data.get('description', ''),
        total_debit=total_debit,
        total_credit=total_credit,
        created_by=get_current_employee_id(),
        status=data.get('status', 'draft')
    )
    db.session.add(entry)
    db.session.flush()

    for item in items:
        ji = JournalEntryItem(
            journal_entry_id=entry.journal_entry_id,
            account_id=item['account_id'],
            debit_amount=item.get('debit_amount', 0),
            credit_amount=item.get('credit_amount', 0),
            description=item.get('description', '')
        )
        db.session.add(ji)

    db.session.commit()
    log_operation('finance', 'create', 'JournalEntry', entry.journal_entry_id, data.get('voucher_no', ''))
    return jsonify(success_response({'journal_entry_id': entry.journal_entry_id}, '凭证添加成功'))


@bp.route('/api/journal-entries/<int:id>/post', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def post_journal_entry(id):
    entry = JournalEntry.query.get_or_404(id)
    if entry.status != 'draft':
        return error_response('只能过账草稿状态的凭证')
    if float(entry.total_debit) != float(entry.total_credit):
        return error_response('借贷不平衡，无法过账')

    # Account types where debit increases balance: asset, expense
    # Account types where credit increases balance: liability, equity, revenue
    DEBIT_INCREASE = {'asset', 'expense', '资产', '费用', '成本'}
    CREDIT_INCREASE = {'liability', 'equity', 'revenue', '负债', '权益', '收入'}

    entry.status = 'posted'
    for item in entry.items:
        account = Account.query.get(item.account_id)
        if not account:
            continue
        atype = (account.account_type or '').lower()
        debit = float(item.debit_amount or 0)
        credit = float(item.credit_amount or 0)
        delta = 0
        if atype in DEBIT_INCREASE:
            delta = debit - credit
        elif atype in CREDIT_INCREASE:
            delta = credit - debit
        else:
            delta = debit - credit  # fallback to default behavior
        account.balance = float(account.balance or 0) + delta

    db.session.commit()
    log_operation('finance', 'post', 'JournalEntry', id, entry.voucher_no)
    return jsonify(success_response(message='过账成功'))


@bp.route('/api/journal-entries/<int:id>', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def update_journal_entry(id):
    entry = JournalEntry.query.get_or_404(id)
    if entry.status != 'draft':
        return error_response('只能编辑草稿状态的凭证')
    data, err = get_json()
    if err: return err
    for field in ['entry_date', 'description']:
        if field in data:
            setattr(entry, field, data[field])
    if 'entry_date' in data:
        try:
            entry.entry_date = datetime.strptime(data['entry_date'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass
    if 'items' in data:
        JournalEntryItem.query.filter_by(journal_entry_id=id).delete()
        total_debit = 0
        total_credit = 0
        for item in data['items']:
            d = float(item.get('debit_amount', 0) or 0)
            c = float(item.get('credit_amount', 0) or 0)
            if d == 0 and c == 0:
                return error_response('每行分录必须填写借方或贷方金额')
            if d > 0 and c > 0:
                return error_response('每行分录不能同时填写借方和贷方金额')
            total_debit += d
            total_credit += c
            ji = JournalEntryItem(
                journal_entry_id=id,
                account_id=item['account_id'],
                debit_amount=d,
                credit_amount=c,
                description=item.get('description', '')
            )
            db.session.add(ji)
        if abs(total_debit - total_credit) > 0.01:
            return error_response('借贷不平衡，借方合计必须等于贷方合计')
        entry.total_debit = total_debit
        entry.total_credit = total_credit
    db.session.commit()
    log_operation('finance', 'update', 'JournalEntry', id, data.get('voucher_no') or entry.voucher_no)
    return jsonify(success_response(message='凭证更新成功'))


@bp.route('/api/journal-entries/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('finance:crud')
def delete_journal_entry(id):
    try:
        JournalEntryItem.query.filter_by(journal_entry_id=id).delete()
        JournalEntry.query.filter_by(journal_entry_id=id).delete()
        db.session.commit()
        log_operation('finance', 'delete', 'JournalEntry', id)
        return jsonify(success_response(message='凭证删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，凭证可能存在关联数据')


# ==================== Budgets ====================

@bp.route('/api/budgets', methods=['GET'])
@require_auth
def get_budgets():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    q = Budget.query.options(joinedload(Budget.account))
    total = q.count()
    rows = q.order_by(Budget.budget_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'budget_id': r.budget_id,
        'budget_period': r.budget_period,
        'account_id': r.account_id,
        'account_name': r.account.account_name if r.account else '',
        'planned_amount': float(r.planned_amount),
        'actual_amount': float(r.actual_amount),
        'variance': float(r.variance) if r.variance else None,
        'status': r.status
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/budgets', methods=['POST'])
@require_auth
@require_permission('finance:crud')
def add_budget():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'budget_period', 'account_id', 'planned_amount')
    if missing: return error_response(f'缺少必填字段: {missing}')
    b = Budget(
        budget_period=data['budget_period'],
        account_id=data['account_id'],
        planned_amount=data['planned_amount'],
        actual_amount=data.get('actual_amount', 0),
        status=data.get('status', 'draft')
    )
    b.variance = float(b.actual_amount) - float(b.planned_amount)
    db.session.add(b)
    db.session.commit()
    log_operation('finance', 'create', 'Budget', b.budget_id, data.get('budget_period', ''))
    return jsonify(success_response({'budget_id': b.budget_id}, '预算添加成功'))


@bp.route('/api/budgets/<int:id>', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def update_budget(id):
    b = Budget.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['budget_period', 'account_id', 'planned_amount', 'actual_amount', 'status']:
        if field in data:
            setattr(b, field, data[field])
    if 'actual_amount' in data or 'planned_amount' in data:
        b.variance = float(b.actual_amount) - float(b.planned_amount)
    db.session.commit()
    log_operation('finance', 'update', 'Budget', id, data.get('budget_period') or b.budget_period)
    return jsonify(success_response(message='预算更新成功'))


@bp.route('/api/budgets/<int:id>/approve', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def approve_budget(id):
    b = Budget.query.get_or_404(id)
    if b.status != 'draft':
        return error_response('只能审批草稿状态的预算')
    b.status = 'approved'
    b.approved_by = get_current_employee_id()
    db.session.commit()
    log_operation('finance', 'approve', 'Budget', id, b.budget_period)
    return jsonify(success_response(message='预算审批成功'))


@bp.route('/api/budgets/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('finance:crud')
def delete_budget(id):
    try:
        Budget.query.filter_by(budget_id=id).delete()
        db.session.commit()
        log_operation('finance', 'delete', 'Budget', id)
        return jsonify(success_response(message='预算删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，预算记录可能存在关联数据')


# ==================== Tax Declarations ====================

@bp.route('/api/tax-declarations', methods=['GET'])
@require_auth
def get_tax_declarations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    q = TaxDeclaration.query
    total = q.count()
    rows = q.order_by(TaxDeclaration.tax_declaration_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'tax_declaration_id': r.tax_declaration_id,
        'tax_type': r.tax_type,
        'declaration_period': r.declaration_period,
        'tax_amount': float(r.tax_amount),
        'paid_amount': float(r.paid_amount),
        'payment_status': r.payment_status,
        'submitted_to': r.submitted_to,
        'submission_date': r.submission_date.isoformat() if r.submission_date else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/tax-declarations', methods=['POST'])
@require_auth
@require_permission('finance:crud')
def add_tax_declaration():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'tax_type', 'declaration_period', 'tax_amount')
    if missing: return error_response(f'缺少必填字段: {missing}')
    td = TaxDeclaration(
        tax_type=data['tax_type'],
        declaration_period=data['declaration_period'],
        tax_amount=data['tax_amount'],
        paid_amount=data.get('paid_amount', 0),
        payment_status=data.get('payment_status', 'unpaid'),
        submitted_to=data.get('submitted_to', ''),
        submission_date=datetime.strptime(data['submission_date'], '%Y-%m-%d').date() if data.get('submission_date') else None
    )
    db.session.add(td)
    db.session.commit()
    log_operation('finance', 'create', 'TaxDeclaration', td.tax_declaration_id)
    return jsonify(success_response({'tax_declaration_id': td.tax_declaration_id}, '税务申报添加成功'))


@bp.route('/api/tax-declarations/<int:id>', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def update_tax_declaration(id):
    td = TaxDeclaration.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['tax_type', 'declaration_period', 'tax_amount', 'paid_amount', 'payment_status', 'submitted_to']:
        if field in data:
            setattr(td, field, data[field])
    if 'submission_date' in data and data['submission_date']:
        td.submission_date = datetime.strptime(data['submission_date'], '%Y-%m-%d').date()
    db.session.commit()
    log_operation('finance', 'update', 'TaxDeclaration', id)
    return jsonify(success_response(message='税务申报更新成功'))


@bp.route('/api/tax-declarations/<int:id>/approve', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def approve_tax_declaration(id):
    td = TaxDeclaration.query.get_or_404(id)
    if td.payment_status == 'paid':
        return error_response('已缴税不可重复审批')
    td.approved_by = get_current_employee_id()
    db.session.commit()
    log_operation('finance', 'approve', 'TaxDeclaration', id)
    return jsonify(success_response(message='税务申报审批成功'))


@bp.route('/api/tax-declarations/<int:id>/pay', methods=['PUT'])
@require_auth
@require_permission('finance:crud')
def pay_tax_declaration(id):
    td = TaxDeclaration.query.get_or_404(id)
    if td.payment_status == 'paid':
        return error_response('已缴税，无需重复缴纳')
    td.payment_status = 'paid'
    td.paid_amount = td.tax_amount
    td.submission_date = date.today()
    db.session.commit()
    log_operation('finance', 'pay', 'TaxDeclaration', id)
    return jsonify(success_response(message='缴税成功'))


@bp.route('/api/tax-declarations/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('finance:crud')
def delete_tax_declaration(id):
    try:
        TaxDeclaration.query.filter_by(tax_declaration_id=id).delete()
        db.session.commit()
        log_operation('finance', 'delete', 'TaxDeclaration', id)
        return jsonify(success_response(message='税务申报删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，税务申报记录可能存在关联数据')
