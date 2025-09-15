from core.models import db, RolePermission, Permission
from app import app  # Ensure app context is available

# Define role-permission mapping
role_permissions = {
    'admin': [
        'view_products', 'create_product', 'edit_product', 'delete_product',
        'record_sale', 'view_sales',
        'manage_users', 'reset_user_password',
        'view_expenses', 'record_expense',
        'view_stock_changes', 'record_stock_change',
        'access_dashboard', 'logout'
    ],
    'sales_clerk': [
        'view_products', 'record_sale', 'view_sales',
        'view_stock_changes', 'record_stock_change',
        'logout'
    ]
}

with app.app_context():
    for role, codes in role_permissions.items():
        for code in codes:
            exists = RolePermission.query.filter_by(role=role, permission_code=code).first()
            if not exists:
                db.session.add(RolePermission(role=role, permission_code=code, is_allowed=True))
    db.session.commit()
    print("Role permissions seeded successfully.")