from models import db
from datetime import datetime

class CashRecord(db.Model):
    __tablename__ = 'cash_records'
    cash_record_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.order_id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='success')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = db.relationship('SalesOrder', backref='cash_records')
    employee = db.relationship('Employee', backref='cash_records')


class Account(db.Model):
    __tablename__ = 'accounts'
    account_id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(20), unique=True, nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'))
    balance = db.Column(db.Numeric(15, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = db.relationship('Account', remote_side=[account_id], backref='children')


class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    journal_entry_id = db.Column(db.Integer, primary_key=True)
    voucher_no = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    total_debit = db.Column(db.Numeric(15, 2), nullable=False)
    total_credit = db.Column(db.Numeric(15, 2), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('Employee', backref='journal_entries')
    items = db.relationship('JournalEntryItem', backref='journal_entry', cascade='all, delete-orphan')


class JournalEntryItem(db.Model):
    __tablename__ = 'journal_entry_items'
    item_id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entries.journal_entry_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    debit_amount = db.Column(db.Numeric(15, 2), default=0.00)
    credit_amount = db.Column(db.Numeric(15, 2), default=0.00)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship('Account')



class Budget(db.Model):
    __tablename__ = 'budgets'
    budget_id = db.Column(db.Integer, primary_key=True)
    budget_period = db.Column(db.String(20), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.account_id'), nullable=False)
    planned_amount = db.Column(db.Numeric(15, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(15, 2), default=0.00)
    variance = db.Column(db.Numeric(15, 2))
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = db.relationship('Account', backref='budgets')
    approver = db.relationship('Employee', foreign_keys=[approved_by])


class TaxDeclaration(db.Model):
    __tablename__ = 'tax_declarations'
    tax_declaration_id = db.Column(db.Integer, primary_key=True)
    tax_type = db.Column(db.String(50), nullable=False)
    declaration_period = db.Column(db.String(20), nullable=False)
    tax_amount = db.Column(db.Numeric(15, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(15, 2), default=0.00)
    payment_status = db.Column(db.String(20), default='unpaid')
    submitted_to = db.Column(db.String(100))
    submission_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('employees.employee_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    approver = db.relationship('Employee', foreign_keys=[approved_by])
