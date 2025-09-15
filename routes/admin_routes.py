import os
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from core.models import db, User, Product, Permission, RolePermission, Sale
from sqlalchemy import func

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    total_income = db.session.query(func.sum(Sale.quantity * Sale.price_sold)).scalar() or 0.0
    total_income = round(total_income, 2)

    return render_template(
        'Admin/dashboard.html',
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else '',
        total_income=total_income
    )

@admin_routes.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('landing'))

@admin_routes.route('/admin/manage-users')
def manage_users():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template(
        'Admin/manage_users.html',
        users=users,
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else ''
    )

@admin_routes.route('/admin/update-user/<user_id>', methods=['POST'])
def update_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)

    user.username = request.form.get('username', user.username)
    user.email = request.form.get('email', user.email)
    user.role = request.form.get('role', user.role)
    user.is_active = request.form.get('is_active', 'true') == 'true'

    if 'profile_image' in request.files:
        image_file = request.files['profile_image']
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            if user.profile_image:
                old_path = os.path.join(upload_folder, user.profile_image)
                if os.path.exists(old_path):
                    os.remove(old_path)

            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)
            user.profile_image = filename

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@admin_routes.route('/admin/delete-user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)

    if user.profile_image:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        image_path = os.path.join(upload_folder, user.profile_image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

@admin_routes.route('/admin/reset-user-password/<user_id>', methods=['GET', 'POST'])
def reset_user_password(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash('Both password fields are required.', 'danger')
        elif new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password reset successfully.', 'success')
            return redirect(url_for('admin_routes.manage_users'))

    return render_template(
        'Admin/reset_user_password.html',
        username=user.username,
        email=user.email,
        profile_image=user.profile_image,
        user_id=user.id
    )

@admin_routes.route('/admin/create-user', methods=['GET', 'POST'])
def create_user():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        profile_image = None

        if not username or not email or not password or not role:
            flash('All fields except image are required.', 'danger')
            return redirect(url_for('admin_routes.create_user'))

        if 'profile_image' in request.files:
            image_file = request.files['profile_image']
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, filename)
                image_file.save(image_path)
                profile_image = filename

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            profile_image=profile_image,
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin_routes.manage_users'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    return render_template(
        'Admin/create_user.html',
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else ''
    )

@admin_routes.route('/admin/create-product', methods=['GET', 'POST'])
def create_product():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        image_path = None

        if not name or not price or not stock:
            flash('Name, price, and stock are required.', 'danger')
            return redirect(url_for('admin_routes.create_product'))

        if 'image_path' in request.files:
            image_file = request.files['image_path']
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'products')
                os.makedirs(upload_folder, exist_ok=True)
                image_path_full = os.path.join(upload_folder, filename)
                image_file.save(image_path_full)
                image_path = filename

        new_product = Product(
            name=name,
            description=description,
            price=float(price),
            stock=int(stock),
            image_path=image_path
        )

        db.session.add(new_product)
        db.session.commit()
        flash('Product created successfully.', 'success')
        return redirect(url_for('admin_routes.view_products'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    return render_template(
        'Admin/create_product.html',
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else ''
    )

@admin_routes.route('/admin/view-products')
def view_products():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    products = Product.query.order_by(Product.created_at.desc()).all()

    return render_template(
        'Admin/view_products.html',
        products=products,
        username=user.username if user else '',
        email=user.email if user else '',
        profile_image=user.profile_image if user else ''
    )

@admin_routes.route('/admin/update-products', methods=['POST'])
def update_products():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    products = Product.query.all()
    upload_folder = os.path.join(current_app.root_path, 'static', 'products')
    os.makedirs(upload_folder, exist_ok=True)

    for product in products:
        product_id = product.id

        product.name = request.form.get(f'name_{product_id}', product.name)
        product.description = request.form.get(f'description_{product_id}', product.description)
        product.price = float(request.form.get(f'price_{product_id}', product.price))
        product.stock = int(request.form.get(f'stock_{product_id}', product.stock))

        image_field = f'image_{product_id}'
        if image_field in request.files:
            image_file = request.files[image_field]
            if image_file and image_file.filename:
                filename = secure_filename(image_file.filename)

                if product.image_path:
                    old_path = os.path.join(upload_folder, product.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                image_path_full = os.path.join(upload_folder, filename)
                image_file.save(image_path_full)
                product.image_path = filename

    db.session.commit()
    flash('All product changes saved successfully.', 'success')
    return redirect(url_for('admin_routes.view_products'))

@admin_routes.route('/admin/delete-product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    product = Product.query.get_or_404(product_id)

    if product.image_path:
        upload_folder = os.path.join(current_app.root_path, 'static', 'products')
        image_path = os.path.join(upload_folder, product.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin_routes.view_products'))

@admin_routes.route('/admin/define-permissions', methods=['GET', 'POST'])
def define_permissions():
    roles_query = db.session.query(User.role).distinct().all()
    roles = [r[0] for r in roles_query if r[0]]

    selected_role = request.form.get('role') if request.method == 'POST' else (roles[0] if roles else None)

    if not selected_role:
        flash("No roles found in the system.", "warning")
        return render_template('Admin/define_permissions.html', roles=[], selected_role=None, permissions=[])

    all_permissions = Permission.query.all()
    role_perms = RolePermission.query.filter_by(role=selected_role).all()
    allowed_codes = {rp.permission_code for rp in role_perms if rp.is_allowed}

    if request.method == 'POST':
        for perm in all_permissions:
            code = perm.code
            is_checked = f'perm_{code}' in request.form
            existing = RolePermission.query.filter_by(role=selected_role, permission_code=code).first()
            if existing:
                existing.is_allowed = is_checked
            else:
                new_perm = RolePermission(role=selected_role, permission_code=code, is_allowed=is_checked)
                db.session.add(new_perm)
        db.session.commit()
        flash(f"Permissions updated for role: {selected_role}", "success")
        return redirect(url_for('admin_routes.define_permissions'))

    for perm in all_permissions:
        perm.is_allowed = perm.code in allowed_codes

    return render_template(
        'Admin/define_permissions.html',
        roles=roles,
        selected_role=selected_role,
        permissions=all_permissions
    )

@admin_routes.route('/admin/system-settings', methods=['GET', 'POST'])
def system_settings():
    if session.get('role') != 'admin':
        return redirect(url_for('shared_routes.login'))

    from core.models import SystemSetting

    settings = SystemSetting.query.first()
    if not settings:
        settings = SystemSetting()
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.system_name = request.form.get('system_name')
        settings.organization_name = request.form.get('organization_name')
        settings.contact_email = request.form.get('contact_email')
        settings.currency = request.form.get('currency')
        settings.timezone = request.form.get('timezone')
        settings.date_format = request.form.get('date_format')
        settings.session_timeout = int(request.form.get('session_timeout') or 30)
        settings.maintenance_mode = 'maintenance_mode' in request.form
        settings.maintenance_message = request.form.get('maintenance_message')
        settings.enable_csv_export = 'enable_csv_export' in request.form
        settings.backup_frequency = request.form.get('backup_frequency')

        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and logo_file.filename:
                filename = secure_filename(logo_file.filename)
                logo_folder = os.path.join(current_app.root_path, 'static', 'logo')
                os.makedirs(logo_folder, exist_ok=True)
                logo_path = os.path.join(logo_folder, filename)
                logo_file.save(logo_path)
                settings.logo_filename = filename

        db.session.commit()
        flash("System settings updated successfully.", "success")
        return redirect(url_for('admin_routes.system_settings'))

    return render_template('Admin/system_settings.html', settings=settings)