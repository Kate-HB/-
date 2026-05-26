from models import db
from datetime import datetime

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    order_id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=0)
    amount_received = db.Column(db.Numeric(12, 2), nullable=True)
    change_amount = db.Column(db.Numeric(12, 2), default=0)
    payment_method = db.Column(db.String(30))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    member = db.relationship('Member', backref='orders')
    employee = db.relationship('Employee', backref='sales_orders')
    items = db.relationship('SalesOrderItem', backref='order', cascade='all, delete-orphan')


class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.order_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')


class SalesReturn(db.Model):
    __tablename__ = 'sales_returns'
    return_id = db.Column(db.Integer, primary_key=True)
    original_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.order_id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'), nullable=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    return_amount = db.Column(db.Numeric(15, 2), nullable=False)
    reason = db.Column(db.Text)
    return_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    original_order = db.relationship('SalesOrder', foreign_keys=[original_order_id], backref='returns')
    member = db.relationship('Member', backref='returns')
    employee = db.relationship('Employee', foreign_keys=[employee_id], backref='sales_returns')
    approver = db.relationship('Employee', foreign_keys=[approved_by])
    items = db.relationship('SalesReturnItem', backref='sales_return', cascade='all, delete-orphan')


class SalesReturnItem(db.Model):
    __tablename__ = 'sales_return_items'
    return_id = db.Column(db.Integer, db.ForeignKey('sales_returns.return_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    refund_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')


class SalesStatistic(db.Model):
    __tablename__ = 'sales_statistics'
    stat_id = db.Column(db.Integer, primary_key=True)
    stat_period = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    order_count = db.Column(db.Integer, nullable=False)
    product_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


