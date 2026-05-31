from models import db
from datetime import datetime

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    warehouse_id = db.Column(db.Integer, primary_key=True)
    warehouse_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    capacity = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    safety_stock = db.Column(db.Integer, default=10)
    last_restock_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref='inventory_records')
    warehouse = db.relationship('Warehouse', backref='inventory_records')


class InventoryDetail(db.Model):
    __tablename__ = 'inventory_details'
    inventory_detail_id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    batch_no = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=0)
    bin_location = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    last_movement_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    warehouse = db.relationship('Warehouse')
    product = db.relationship('Product')


class InboundRecord(db.Model):
    __tablename__ = 'inbound_records'
    inbound_record_id = db.Column(db.Integer, primary_key=True)
    inbound_no = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'), nullable=False)
    total_quantity = db.Column(db.Integer, default=0)
    inbound_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.order_id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier')
    warehouse = db.relationship('Warehouse')
    purchase_order = db.relationship('PurchaseOrder', backref='inbound_records')
    creator = db.relationship('Employee', foreign_keys=[created_by])
    items = db.relationship('InboundItem', backref='inbound_record', cascade='all, delete-orphan')


class InboundItem(db.Model):
    __tablename__ = 'inbound_items'
    inbound_record_id = db.Column(db.Integer, db.ForeignKey('inbound_records.inbound_record_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    batch_no = db.Column(db.String(50), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2))
    expiry_date = db.Column(db.Date)
    bin_location = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')


class OutboundRecord(db.Model):
    __tablename__ = 'outbound_records'
    outbound_record_id = db.Column(db.Integer, primary_key=True)
    outbound_no = db.Column(db.String(50), unique=True, nullable=False)
    source_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.order_id'), nullable=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id'), nullable=False)
    total_quantity = db.Column(db.Integer, default=0)
    outbound_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source_order = db.relationship('SalesOrder', foreign_keys=[source_order_id])
    warehouse = db.relationship('Warehouse')
    creator = db.relationship('Employee', foreign_keys=[created_by])
    approver = db.relationship('Employee', foreign_keys=[approved_by])
    items = db.relationship('OutboundItem', backref='outbound_record', cascade='all, delete-orphan')


class OutboundItem(db.Model):
    __tablename__ = 'outbound_items'
    outbound_record_id = db.Column(db.Integer, db.ForeignKey('outbound_records.outbound_record_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    batch_no = db.Column(db.String(50), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    bin_location = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
