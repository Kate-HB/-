from models import db
from datetime import datetime

class Position(db.Model):
    __tablename__ = 'positions'
    position_id = db.Column(db.Integer, primary_key=True)
    position_name = db.Column(db.String(80), nullable=False)
    responsibilities = db.Column(db.Text)
    salary_grade = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(50), nullable=False)
    employee_no = db.Column(db.String(20), unique=True, nullable=False)
    id_card = db.Column(db.String(18))
    department = db.Column(db.String(50))
    position_id = db.Column(db.Integer, db.ForeignKey('positions.position_id'))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    hire_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    position = db.relationship('Position', backref='employees')


class Schedule(db.Model):
    __tablename__ = 'schedules'
    schedule_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    shift_type = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='schedules')
    creator = db.relationship('Employee', foreign_keys=[created_by])


class Attendance(db.Model):
    __tablename__ = 'attendances'
    attendance_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.schedule_id'))
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)
    leave_type = db.Column(db.String(20))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', backref='attendances')
    schedule = db.relationship('Schedule', backref='attendances')


class Payroll(db.Model):
    __tablename__ = 'payrolls'
    payroll_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    pay_period = db.Column(db.String(10), nullable=False)
    base_salary = db.Column(db.Numeric(12, 2), nullable=False)
    bonus = db.Column(db.Numeric(12, 2), default=0)
    deduction = db.Column(db.Numeric(12, 2), default=0)
    net_pay = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    generated_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='payrolls')
    generator = db.relationship('Employee', foreign_keys=[generated_by])
