from models import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80), nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent = db.relationship('Category', remote_side=[category_id], backref='children')


class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    cost_price = db.Column(db.Numeric(12, 2), nullable=True)
    barcode = db.Column(db.String(50), nullable=True)
    spec = db.Column(db.String(255))
    unit = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', backref='products')
    supplier = db.relationship('Supplier', backref='products')



class Promotion(db.Model):
    __tablename__ = 'promotions'
    promotion_id = db.Column(db.Integer, primary_key=True)
    promotion_name = db.Column(db.String(120), nullable=False)
    promotion_type = db.Column(db.String(20), nullable=False)
    discount_rate = db.Column(db.Numeric(5, 4), nullable=True)
    fixed_amount = db.Column(db.Numeric(12, 2), nullable=True)
    min_amount = db.Column(db.Numeric(12, 2), nullable=True)
    min_quantity = db.Column(db.Integer, nullable=True)
    gift_quantity = db.Column(db.Integer, nullable=True, default=1)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    approved_by = db.Column(db.Integer, nullable=True)
    points_earned = db.Column(db.Integer, default=0)
    gift_product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=True)
    status = db.Column(db.String(20), default='pending')
    gift_product = db.relationship('Product', foreign_keys=[gift_product_id])

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PromotionProduct(db.Model):
    __tablename__ = 'promotion_products'
    promotion_id = db.Column(db.Integer, db.ForeignKey('promotions.promotion_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), primary_key=True)
    specific_discount = db.Column(db.Numeric(5, 4), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    promotion = db.relationship('Promotion', backref='promotion_products')
    product = db.relationship('Product')
