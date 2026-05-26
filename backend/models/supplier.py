from models import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    credit_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SupplierContract(db.Model):
    __tablename__ = 'supplier_contracts'
    contract_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    contract_type = db.Column(db.String(50))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(20), default='pending')
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    signed_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', backref='contracts')
    approver = db.relationship('Employee', foreign_keys=[approved_by])


class SupplierEvaluation(db.Model):
    __tablename__ = 'supplier_evaluations'
    evaluation_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    score = db.Column(db.Numeric(4, 2), nullable=False)
    quality_score = db.Column(db.Numeric(4, 2))
    delivery_score = db.Column(db.Numeric(4, 2))
    service_score = db.Column(db.Numeric(4, 2))
    evaluation_date = db.Column(db.Date, nullable=False)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    supplier = db.relationship('Supplier', backref='evaluations')
    evaluator = db.relationship('Employee', foreign_keys=[evaluator_id])
