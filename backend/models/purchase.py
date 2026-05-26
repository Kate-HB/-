from models import db
from datetime import datetime

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    order_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('supplier_contracts.contract_id'), nullable=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default='draft')
    delivery_date = db.Column(db.Date)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'))
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    notes = db.Column(db.Text)
    payment_status = db.Column(db.String(20), default='unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref='purchase_orders')
    contract = db.relationship('SupplierContract', backref='purchase_orders')
    warehouse = db.relationship('Warehouse', backref='purchase_orders')
    creator = db.relationship('Employee', foreign_keys=[created_by], backref='created_purchases')
    approver = db.relationship('Employee', foreign_keys=[approved_by], backref='approved_purchases')
    items = db.relationship('PurchaseOrderItem', backref='order', cascade='all, delete-orphan')


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.order_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
