from flask import Blueprint, render_template, session, redirect, url_for, request
from core.models import db, User, Product, Sale, SystemSetting
from datetime import datetime
from sqlalchemy import text, func

sales_routes = Blueprint('sales_routes', __name__)

def get_total_income():
    total = db.session.query(func.sum(Sale.quantity * Sale.price_sold)).scalar() or 0.0
    return round(total, 2)

@sales_routes.route('/sales/dashboard')
def sales_dashboard():
    if session.get('role') != 'sales_clerk':
        return redirect(url_for('shared_routes.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    total_income = get_total_income()

    return render_template(
        'Sales_Clerk/dashboard.html',
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else '',
        total_income=total_income
    )

@sales_routes.route('/sales/sale_aproduct')
def sale_aproduct():
    if session.get('role') != 'sales_clerk':
        return redirect(url_for('shared_routes.login'))

    user_id = session.get('user_id')
    products = Product.query.all()
    sales = Sale.query.filter_by(seller_id=user_id).order_by(Sale.timestamp.desc()).all()

    total_earned = sum(s.quantity * s.price_sold for s in sales)
    total_income = get_total_income()

    return render_template(
        'Sales_Clerk/sale_aproduct.html',
        products=products,
        sales=sales,
        total_earned=total_earned,
        total_income=total_income
    )

@sales_routes.route('/sales/view-stock')
def view_stock():
    if session.get('role') != 'sales_clerk':
        return redirect(url_for('shared_routes.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    products = Product.query.order_by(Product.name.asc()).all()

    return render_template(
        'Sales_Clerk/view_stock.html',
        products=products,
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else ''
    )

@sales_routes.route('/sales/save_sale', methods=['POST'])
def save_sale():
    if session.get('role') != 'sales_clerk':
        return redirect(url_for('shared_routes.login'))

    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    price_sold = float(request.form.get('price_sold'))
    seller_id = session.get('user_id')

    sale = Sale(
        product_id=product_id,
        seller_id=seller_id,
        quantity=quantity,
        price_sold=price_sold
    )
    db.session.add(sale)

    product = Product.query.get(product_id)
    if product:
        product.stock -= quantity

    db.session.commit()

    return redirect(url_for('sales_routes.sale_receipt', sale_id=sale.id))

@sales_routes.route('/sales/receipt/<sale_id>')
def sale_receipt(sale_id):
    if session.get('role') != 'sales_clerk':
        return redirect(url_for('shared_routes.login'))

    sale = Sale.query.get(sale_id)
    if not sale or sale.seller_id != session.get('user_id'):
        return redirect(url_for('sales_routes.sale_aproduct'))

    product = sale.product
    subtotal = sale.price_sold * sale.quantity
    user = User.query.get(sale.seller_id)
    system = SystemSetting.query.first()

    return render_template(
        'Sales_Clerk/receipt.html',
        sale=sale,
        product=product,
        user=user,
        subtotal=subtotal,
        shop_name="Makindye Shop System",
        location="Entebbe, Kampala",
        system=system
    )

@sales_routes.route('/sales/patch_cost_price')
def patch_cost_price():
    # TEMPORARY PATCH ACCESS — REMOVE AFTER USE
    try:
        db.session.execute(text("ALTER TABLE products ADD COLUMN cost_price FLOAT DEFAULT 0.0;"))
        db.session.commit()
        return "✅ cost_price column added successfully."
    except Exception as e:
        return f"❌ Error: {str(e)}"

@sales_routes.route('/sales/logout')
def sales_logout():
    session.clear()
    return redirect(url_for('landing'))