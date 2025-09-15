from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'seller'
    profile_image = db.Column(db.String(255))  # Path to uploaded profile image
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)  # ✅ New field added

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False, default=0.0)  # Added for profit tracking
    stock = db.Column(db.Integer, default=0)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.name}>"

class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    product_id = db.Column(db.String, db.ForeignKey('products.id'), nullable=False)
    seller_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_sold = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')
    seller = db.relationship('User')

    def __repr__(self):
        return f"<Sale {self.quantity} x {self.product_id} by {self.seller_id}>"

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Expense {self.category}: UGX {self.amount}>"

class StockChange(db.Model):
    __tablename__ = 'stock_changes'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    product_id = db.Column(db.String, db.ForeignKey('products.id'), nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 'restock', 'loss'
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product')

    def __repr__(self):
        return f"<StockChange {self.change_type} {self.quantity} of {self.product_id}>"

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    code = db.Column(db.String(100), unique=True, nullable=False)  # e.g. 'view_products'
    label = db.Column(db.String(150), nullable=False)              # e.g. 'View Products'
    category = db.Column(db.String(100))                           # e.g. 'Products', 'Users'

    def __repr__(self):
        return f"<Permission {self.code}>"

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    role = db.Column(db.String(50), nullable=False)  # e.g. 'admin', 'seller'
    permission_code = db.Column(db.String(100), nullable=False)  # e.g. 'view_products'
    is_allowed = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<RolePermission {self.role} -> {self.permission_code}: {self.is_allowed}>"

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    system_name = db.Column(db.String(100))
    organization_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    currency = db.Column(db.String(10), default='UGX')
    timezone = db.Column(db.String(50), default='Africa/Kampala')
    date_format = db.Column(db.String(20), default='DD/MM/YYYY')
    session_timeout = db.Column(db.Integer, default=30)
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.String(255))
    enable_csv_export = db.Column(db.Boolean, default=True)
    backup_frequency = db.Column(db.String(20), default='weekly')
    logo_filename = db.Column(db.String(255))

    def __repr__(self):
        return f"<SystemSetting {self.system_name}>"