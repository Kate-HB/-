from flask import Blueprint, request, jsonify
from models import db
from models.member import Member, MemberLevel, MemberPointsRecord, PointsPolicy
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime, timezone

bp = Blueprint('members', __name__)


# ==================== Members ====================

@bp.route('/api/members', methods=['GET'])
@require_auth
def get_members():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    q = Member.query
    if search:
        q = q.filter((Member.member_name.contains(search)) | (Member.phone.contains(search)) | (Member.member_no.contains(search)))
    if status:
        q = q.filter(Member.status == status)

    total = q.count()
    rows = q.order_by(Member.member_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'member_id': r.member_id,
        'member_no': r.member_no,
        'member_name': r.member_name,
        'phone': r.phone,
        'email': r.email,
        'level': r.level,
        'points': r.points,
        'register_date': r.register_date.isoformat() if r.register_date else None,
        'status': r.status
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/members', methods=['POST'])
@require_auth
@require_permission('member:crud')
def add_member():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'member_no', 'member_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    member = Member(
        member_no=data['member_no'],
        member_name=data['member_name'],
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        level=data.get('level', '普通会员'),
        points=data.get('points', 0),
        register_date=datetime.strptime(data['register_date'], '%Y-%m-%d').date() if data.get('register_date') else datetime.now(timezone.utc).date(),
        status=data.get('status', 'active')
    )
    db.session.add(member)
    db.session.commit()
    log_operation('member', 'create', 'Member', member.member_id, data.get('member_name', ''))
    return jsonify(success_response({'member_id': member.member_id}, '会员添加成功'))


@bp.route('/api/members/<int:id>', methods=['PUT'])
@require_auth
@require_permission('member:crud')
def update_member(id):
    member = Member.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['member_no', 'member_name', 'phone', 'email', 'level', 'status']:
        if field in data:
            setattr(member, field, data[field])
    if 'register_date' in data and data['register_date']:
        member.register_date = datetime.strptime(data['register_date'], '%Y-%m-%d').date()
    db.session.commit()
    log_operation('member', 'update', 'Member', id, data.get('member_name') or member.member_name)
    return jsonify(success_response(message='会员更新成功'))


@bp.route('/api/members/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('member:crud')
def delete_member(id):
    try:
        from models.sales import SalesOrder, SalesReturn
        SalesOrder.query.filter_by(member_id=id).update({'member_id': None})
        SalesReturn.query.filter_by(member_id=id).update({'member_id': None})
        MemberPointsRecord.query.filter_by(member_id=id).delete()
        Member.query.filter_by(member_id=id).delete()
        db.session.commit()
        log_operation('member', 'delete', 'Member', id)
        return jsonify(success_response(message='删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，可能存在关联数据')


# ==================== Member Levels ====================

@bp.route('/api/member-levels', methods=['GET'])
@require_auth
def get_member_levels():
    rows = MemberLevel.query.all()
    result = [{
        'level_id': r.level_id,
        'level_name': r.level_name,
        'upgrade_condition': r.upgrade_condition,
        'discount_rate': float(r.discount_rate) if r.discount_rate else None,
        'points_multiplier': float(r.points_multiplier) if r.points_multiplier else None,
        'description': r.description
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/member-levels', methods=['POST'])
@require_auth
@require_permission('member:crud')
def add_member_level():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'level_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    level = MemberLevel(
        level_name=data['level_name'],
        upgrade_condition=data.get('upgrade_condition', ''),
        discount_rate=data.get('discount_rate'),
        points_multiplier=data.get('points_multiplier', 1.0),
        description=data.get('description', '')
    )
    db.session.add(level)
    db.session.commit()
    log_operation('member', 'create', 'MemberLevel', level.level_id, data.get('level_name', ''))
    return jsonify(success_response({'level_id': level.level_id}, '会员等级添加成功'))


@bp.route('/api/member-levels/<int:id>', methods=['PUT'])
@require_auth
@require_permission('member:crud')
def update_member_level(id):
    level = MemberLevel.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['level_name', 'upgrade_condition', 'discount_rate', 'points_multiplier', 'description']:
        if field in data:
            setattr(level, field, data[field])
    db.session.commit()
    log_operation('member', 'update', 'MemberLevel', id, data.get('level_name') or level.level_name)
    return jsonify(success_response(message='会员等级更新成功'))


@bp.route('/api/member-levels/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('member:crud')
def delete_member_level(id):
    try:
        from models.member import Member
        Member.query.filter_by(level=MemberLevel.query.get_or_404(id).level_name).update({'level': '普通会员'})
        MemberLevel.query.filter_by(level_id=id).delete()
        db.session.commit()
        log_operation('member', 'delete', 'MemberLevel', id, data.get('level_name') or level.level_name)
        return jsonify(success_response(message='会员等级删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，该等级可能有关联会员')


# ==================== Member Points ====================

@bp.route('/api/member-points', methods=['GET'])
@require_auth
def get_member_points():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    member_id = request.args.get('member_id', type=int)

    q = MemberPointsRecord.query
    if member_id:
        q = q.filter(MemberPointsRecord.member_id == member_id)

    total = q.count()
    rows = q.order_by(MemberPointsRecord.record_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'record_id': r.record_id,
        'member_id': r.member_id,
        'member_name': r.member.member_name,
        'points_change': r.points_change,
        'change_type': r.change_type,
        'related_order_id': r.related_order_id,
        'change_date': r.change_date.isoformat() if r.change_date else None,
        'remarks': r.remarks
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/member-points', methods=['POST'])
@require_auth
@require_permission('member:crud')
def add_member_points():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'member_id', 'change_type', 'points_change')
    if missing: return error_response(f'缺少必填字段: {missing}')
    record = MemberPointsRecord(
        member_id=data['member_id'],
        points_change=data['points_change'],
        change_type=data.get('change_type', 'adjust'),
        related_order_id=data.get('related_order_id'),
        change_date=datetime.fromisoformat(data['change_date']) if data.get('change_date') else datetime.now(timezone.utc),
        remarks=data.get('remarks', ''),
        created_by=get_current_employee_id()
    )
    db.session.add(record)

    if data['change_type'] not in ('earn', 'redeem', 'adjust', 'expire'):
        return error_response('无效的变更类型')
    if data['change_type'] == 'redeem' and data['points_change'] > 0:
        return error_response('兑换积分时积分变动必须为负数')
    if data['change_type'] == 'earn' and data['points_change'] < 0:
        return error_response('获取积分时积分变动必须为正数')
    member = Member.query.get(data['member_id'])
    if member:
        new_points = (member.points or 0) + data['points_change']
        if new_points < 0:
            return error_response('积分不足，当前积分: ' + str(member.points or 0))
        member.points = (member.points or 0) + data['points_change']

    db.session.commit()
    log_operation('member', 'create', 'MemberPointsRecord', record.record_id)
    return jsonify(success_response({'record_id': record.record_id}, '积分调整成功'))
