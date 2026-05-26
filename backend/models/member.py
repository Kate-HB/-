from models import db
from datetime import datetime

class Member(db.Model):
    __tablename__ = 'members'
    member_id = db.Column(db.Integer, primary_key=True)
    member_no = db.Column(db.String(50), unique=True, nullable=False)
    member_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    level = db.Column(db.String(20), default='普通会员')
    points = db.Column(db.Integer, default=0)
    register_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberLevel(db.Model):
    __tablename__ = 'member_levels'
    level_id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(50), nullable=False)
    upgrade_condition = db.Column(db.String(200))
    discount_rate = db.Column(db.Numeric(5, 4))
    points_multiplier = db.Column(db.Numeric(5, 2), default=1.00)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberPointsRecord(db.Model):
    __tablename__ = 'member_points_records'
    record_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=False)
    points_change = db.Column(db.Integer, nullable=False)
    change_type = db.Column(db.String(20), nullable=False)
    related_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.order_id'), nullable=True)
    change_date = db.Column(db.DateTime, nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)

    member = db.relationship('Member', backref='points_records')
    related_order = db.relationship('SalesOrder', foreign_keys=[related_order_id])
    creator = db.relationship('Employee', foreign_keys=[created_by])


class PointsPolicy(db.Model):
    __tablename__ = 'points_policies'
    policy_id = db.Column(db.Integer, primary_key=True)
    policy_name = db.Column(db.String(100), nullable=False)
    earn_rule = db.Column(db.Text)
    redeem_rule = db.Column(db.Text)
    valid_period = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberLevelPolicy(db.Model):
    __tablename__ = 'member_level_policies'
    level_id = db.Column(db.Integer, db.ForeignKey('member_levels.level_id'), primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('points_policies.policy_id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    level = db.relationship('MemberLevel')
    policy = db.relationship('PointsPolicy')
