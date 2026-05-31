from flask import Blueprint, request, jsonify
from models import db
from models.employee import Position, Employee, Schedule, Attendance, Payroll
from utils.errors import success_response, error_response, get_json, require_fields
from utils.auth import require_auth, require_permission, get_current_employee_id
from utils.operation_log import log_operation
from datetime import datetime, date
from sqlalchemy.orm import joinedload

bp = Blueprint('employees', __name__)

DEPARTMENTS = ['生鲜部', '食品部', '日用品部', '家电部', '服装部', '收银部', '仓储部', '采购部', '销售部', '行政部', '财务部', '人事部']


# ==================== Departments ====================

@bp.route('/api/departments', methods=['GET'])
@require_auth
def get_departments():
    return jsonify(success_response([{'value': d, 'label': d} for d in DEPARTMENTS]))


# ==================== Employees ====================

@bp.route('/api/employees', methods=['GET'])
@require_auth
def get_employees():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    department = request.args.get('department', '')

    q = Employee.query.options(joinedload(Employee.position))
    if search:
        q = q.filter((Employee.employee_name.contains(search)) | (Employee.employee_no.contains(search)))
    if status:
        q = q.filter(Employee.status == status)
    if department:
        q = q.filter(Employee.department == department)

    total = q.count()
    rows = q.order_by(Employee.employee_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'employee_id': r.employee_id,
        'employee_no': r.employee_no,
        'employee_name': r.employee_name,
        'id_card': r.id_card,
        'department': r.department,
        'position_id': r.position_id,
        'position_name': r.position.position_name if r.position else '',
        'phone': r.phone,
        'email': r.email,
        'status': r.status,
        'hire_date': r.hire_date.isoformat() if r.hire_date else None
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/employees', methods=['POST'])
@require_auth
@require_permission('employee:crud')
def add_employee():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_no', 'employee_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    emp = Employee(
        employee_no=data['employee_no'],
        employee_name=data['employee_name'],
        id_card=data.get('id_card', ''),
        department=data.get('department', ''),
        position_id=data.get('position_id'),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        status=data.get('status', 'active'),
        hire_date=datetime.strptime(data['hire_date'], '%Y-%m-%d').date() if data.get('hire_date') else date.today()
    )
    db.session.add(emp)
    db.session.commit()
    log_operation('employee', 'create', 'Employee', emp.employee_id, data.get('employee_name', ''))
    return jsonify(success_response({'employee_id': emp.employee_id}, '员工添加成功'))


@bp.route('/api/employees/<int:id>', methods=['PUT'])
@require_auth
@require_permission('employee:crud')
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['employee_no', 'employee_name', 'id_card', 'department', 'position_id', 'phone', 'email', 'status']:
        if field in data:
            setattr(emp, field, data[field])
    if 'hire_date' in data and data['hire_date']:
        emp.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
    db.session.commit()
    log_operation('employee', 'update', 'Employee', id, data.get('employee_name') or emp.employee_name)
    return jsonify(success_response(message='员工更新成功'))


@bp.route('/api/employees/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('employee:crud')
def delete_employee(id):
    try:
        from models.user import User
        from models.sales import SalesOrder, SalesReturn
        from models.finance import CashRecord, JournalEntry, Budget
        from models.purchase import PurchaseOrder
        from models.warehouse import InboundRecord, OutboundRecord
        # Set nullable FKs to NULL
        User.query.filter_by(employee_id=id).update({'employee_id': None})
        SalesOrder.query.filter_by(employee_id=id).update({'employee_id': None})
        SalesReturn.query.filter_by(employee_id=id).update({'employee_id': None})
        CashRecord.query.filter_by(employee_id=id).update({'employee_id': None})
        JournalEntry.query.filter_by(created_by=id).update({'created_by': None})
        Budget.query.filter_by(approved_by=id).update({'approved_by': None})
        InboundRecord.query.filter_by(created_by=id).update({'created_by': None})
        OutboundRecord.query.filter_by(created_by=id).update({'created_by': None})
        PurchaseOrder.query.filter_by(created_by=id).update({'created_by': None})
        PurchaseOrder.query.filter_by(approved_by=id).update({'approved_by': None})
        # Delete child records
        Schedule.query.filter_by(employee_id=id).delete()
        Attendance.query.filter_by(employee_id=id).delete()
        Payroll.query.filter_by(employee_id=id).delete()
        Employee.query.filter_by(employee_id=id).delete()
        db.session.commit()
        log_operation('employee', 'delete', 'Employee', id)
        return jsonify(success_response(message='删除成功'))
    except Exception as e:
        db.session.rollback()
        return error_response('删除失败，可能存在关联数据')


# ==================== Positions ====================

@bp.route('/api/positions', methods=['GET'])
@require_auth
def get_positions():
    rows = Position.query.all()
    result = [{
        'position_id': r.position_id,
        'position_name': r.position_name,
        'responsibilities': r.responsibilities,
        'salary_grade': r.salary_grade
    } for r in rows]
    return jsonify(success_response(result))


@bp.route('/api/positions', methods=['POST'])
@require_auth
@require_permission('employee:crud')
def add_position():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'position_name')
    if missing: return error_response(f'缺少必填字段: {missing}')
    pos = Position(
        position_name=data['position_name'],
        responsibilities=data.get('responsibilities', ''),
        salary_grade=data.get('salary_grade', '')
    )
    db.session.add(pos)
    db.session.commit()
    log_operation('employee', 'create', 'Position', pos.position_id, data.get('position_name', ''))
    return jsonify(success_response({'position_id': pos.position_id}, '岗位添加成功'))


# ==================== Schedules ====================

@bp.route('/api/schedules', methods=['GET'])
@require_auth
def get_schedules():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    q = Schedule.query.options(joinedload(Schedule.employee))
    total = q.count()
    rows = q.order_by(Schedule.schedule_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'schedule_id': r.schedule_id,
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'work_date': r.work_date.isoformat() if r.work_date else None,
        'shift_type': r.shift_type,
        'start_time': r.start_time.strftime('%H:%M') if r.start_time else '',
        'end_time': r.end_time.strftime('%H:%M') if r.end_time else ''
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/schedules', methods=['POST'])
@require_auth
@require_permission('employee:crud')
def add_schedule():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_id', 'work_date', 'shift_type')
    if missing: return error_response(f'缺少必填字段: {missing}')
    sched = Schedule(
        employee_id=data['employee_id'],
        work_date=datetime.strptime(data['work_date'], '%Y-%m-%d').date() if data.get('work_date') else date.today(),
        shift_type=data['shift_type'],
        start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
        end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
        created_by=get_current_employee_id()
    )
    db.session.add(sched)
    db.session.commit()
    log_operation('employee', 'create', 'Schedule', sched.schedule_id)
    return jsonify(success_response({'schedule_id': sched.schedule_id}, '排班添加成功'))


@bp.route('/api/schedules/<int:id>', methods=['PUT'])
@require_auth
@require_permission('employee:crud')
def update_schedule(id):
    sched = Schedule.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['employee_id', 'shift_type']:
        if field in data:
            setattr(sched, field, data[field])
    if 'work_date' in data and data['work_date']:
        sched.work_date = datetime.strptime(data['work_date'], '%Y-%m-%d').date()
    if 'start_time' in data and data['start_time']:
        sched.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    if 'end_time' in data and data['end_time']:
        sched.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
    db.session.commit()
    log_operation('employee', 'update', 'Schedule', id)
    return jsonify(success_response(message='排班更新成功'))


@bp.route('/api/schedules/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('employee:crud')
def delete_schedule(id):
    try:
        Schedule.query.filter_by(schedule_id=id).delete()
        db.session.commit()
        log_operation('employee', 'delete', 'Schedule', id)
        return jsonify(success_response(message='排班删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，排班记录可能存在关联数据')


# ==================== Attendances ====================

@bp.route('/api/attendances', methods=['GET'])
@require_auth
def get_attendances():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    q = Attendance.query.options(joinedload(Attendance.employee))
    total = q.count()
    rows = q.order_by(Attendance.attendance_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'attendance_id': r.attendance_id,
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'schedule_id': r.schedule_id,
        'check_in_time': r.check_in_time.isoformat() if r.check_in_time else None,
        'check_out_time': r.check_out_time.isoformat() if r.check_out_time else None,
        'status': r.status,
        'leave_type': r.leave_type,
        'remarks': r.remarks
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/attendances', methods=['POST'])
@require_auth
@require_permission('employee:crud')
def add_attendance():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_id', 'status')
    if missing: return error_response(f'缺少必填字段: {missing}')
    att = Attendance(
        employee_id=data['employee_id'],
        schedule_id=data.get('schedule_id'),
        check_in_time=datetime.fromisoformat(data['check_in_time']) if data.get('check_in_time') else None,
        check_out_time=datetime.fromisoformat(data['check_out_time']) if data.get('check_out_time') else None,
        status=data['status'],
        leave_type=data.get('leave_type'),
        remarks=data.get('remarks', '')
    )
    db.session.add(att)
    db.session.commit()
    log_operation('employee', 'create', 'Attendance', att.attendance_id)
    return jsonify(success_response({'attendance_id': att.attendance_id}, '考勤记录添加成功'))


@bp.route('/api/attendances/<int:id>', methods=['PUT'])
@require_auth
@require_permission('employee:crud')
def update_attendance(id):
    att = Attendance.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['employee_id', 'schedule_id', 'status', 'leave_type', 'remarks']:
        if field in data:
            setattr(att, field, data[field])
    if 'check_in_time' in data and data['check_in_time']:
        att.check_in_time = datetime.fromisoformat(data['check_in_time'])
    if 'check_out_time' in data and data['check_out_time']:
        att.check_out_time = datetime.fromisoformat(data['check_out_time'])
    db.session.commit()
    log_operation('employee', 'update', 'Attendance', id)
    return jsonify(success_response(message='考勤记录更新成功'))


@bp.route('/api/attendances/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('employee:crud')
def delete_attendance(id):
    try:
        Attendance.query.filter_by(attendance_id=id).delete()
        db.session.commit()
        log_operation('employee', 'delete', 'Attendance', id)
        return jsonify(success_response(message='考勤记录删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，考勤记录可能存在关联数据')


# ==================== Payrolls ====================

@bp.route('/api/payrolls', methods=['GET'])
@require_auth
def get_payrolls():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pay_period = request.args.get('pay_period', '')

    q = Payroll.query.options(joinedload(Payroll.employee))
    if pay_period:
        q = q.filter(Payroll.pay_period == pay_period)

    total = q.count()
    rows = q.order_by(Payroll.payroll_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = [{
        'payroll_id': r.payroll_id,
        'employee_id': r.employee_id,
        'employee_name': r.employee.employee_name if r.employee else '',
        'pay_period': r.pay_period,
        'base_salary': float(r.base_salary),
        'bonus': float(r.bonus),
        'deduction': float(r.deduction),
        'net_pay': float(r.net_pay),
        'status': r.status
    } for r in rows]

    return jsonify(success_response(result, page=page, total=total))


@bp.route('/api/payrolls', methods=['POST'])
@require_auth
@require_permission('employee:crud')
def add_payroll():
    data, err = get_json()
    if err: return err
    missing = require_fields(data, 'employee_id', 'pay_period')
    if missing: return error_response(f'缺少必填字段: {missing}')
    try:
        base = float(data['base_salary'])
        bonus = float(data.get('bonus', 0))
        deduction = float(data.get('deduction', 0))
    except (ValueError, TypeError):
        return error_response('工资金额格式不正确')
    if base < 0 or bonus < 0 or deduction < 0:
        return error_response('工资金额不能为负数')
    net_pay = base + bonus - deduction
    if net_pay < 0:
        return error_response('实发工资不能为负数，请检查扣除金额')

    payroll = Payroll(
        employee_id=data['employee_id'],
        pay_period=data['pay_period'],
        base_salary=base,
        bonus=bonus,
        deduction=deduction,
        net_pay=net_pay,
        status=data.get('status', 'pending'),
        generated_by=get_current_employee_id()
    )
    db.session.add(payroll)
    db.session.commit()
    log_operation('employee', 'create', 'Payroll', payroll.payroll_id)
    return jsonify(success_response({'payroll_id': payroll.payroll_id, 'net_pay': net_pay}, '工资记录创建成功'))


@bp.route('/api/payrolls/<int:id>/approve', methods=['PUT'])
@require_auth
@require_permission('employee:crud')
def approve_payroll(id):
    p = Payroll.query.get_or_404(id)
    if p.status != 'pending':
        return error_response('只能审批待处理状态的工资记录')
    p.status = 'paid'
    db.session.commit()
    log_operation('employee', 'approve', 'Payroll', id)
    return jsonify(success_response(message='工资已发放'))


@bp.route('/api/payrolls/<int:id>', methods=['PUT'])
@require_auth
@require_permission('employee:crud')
def update_payroll(id):
    p = Payroll.query.get_or_404(id)
    data, err = get_json()
    if err: return err
    for field in ['employee_id', 'pay_period', 'status']:
        if field in data:
            setattr(p, field, data[field])
    if 'base_salary' in data:
        p.base_salary = data['base_salary']
    if 'bonus' in data:
        p.bonus = data['bonus']
    if 'deduction' in data:
        p.deduction = data['deduction']
    p.net_pay = float(p.base_salary or 0) + float(p.bonus or 0) - float(p.deduction or 0)
    db.session.commit()
    log_operation('employee', 'update', 'Payroll', id)
    return jsonify(success_response(message='工资记录更新成功'))


@bp.route('/api/payrolls/<int:id>', methods=['DELETE'])
@require_auth
@require_permission('employee:crud')
def delete_payroll(id):
    try:
        Payroll.query.filter_by(payroll_id=id).delete()
        db.session.commit()
        log_operation('employee', 'delete', 'Payroll', id)
        return jsonify(success_response(message='工资记录删除成功'))
    except Exception:
        db.session.rollback()
        return error_response('删除失败，工资记录可能存在关联数据')
