from core.models import db, Permission
from app import app  # Ensure app context is available

permissions = [
    # Products
    {'code': 'view_products', 'label': 'View Products', 'category': 'Products'},
    {'code': 'create_product', 'label': 'Create New Product', 'category': 'Products'},
    {'code': 'edit_product', 'label': 'Edit Product Details', 'category': 'Products'},
    {'code': 'delete_product', 'label': 'Delete Product', 'category': 'Products'},

    # Sales
    {'code': 'record_sale', 'label': 'Record a Sale', 'category': 'Sales'},
    {'code': 'view_sales', 'label': 'View Sales History', 'category': 'Sales'},

    # Users
    {'code': 'manage_users', 'label': 'Manage Users & Roles', 'category': 'Users'},
    {'code': 'reset_user_password', 'label': 'Reset User Password', 'category': 'Users'},

    # Finance
    {'code': 'view_expenses', 'label': 'View Expenses', 'category': 'Finance'},
    {'code': 'record_expense', 'label': 'Record Expense', 'category': 'Finance'},

    # Inventory
    {'code': 'view_stock_changes', 'label': 'View Stock Changes', 'category': 'Inventory'},
    {'code': 'record_stock_change', 'label': 'Record Stock Adjustment', 'category': 'Inventory'},

    # System
    {'code': 'access_dashboard', 'label': 'Access Admin Dashboard', 'category': 'System'},
    {'code': 'logout', 'label': 'Logout', 'category': 'System'},
]

with app.app_context():
    for perm in permissions:
        exists = Permission.query.filter_by(code=perm['code']).first()
        if not exists:
            db.session.add(Permission(**perm))
    db.session.commit()
    print("Permissions seeded successfully.")