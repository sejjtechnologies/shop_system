from flask import Blueprint, request, redirect, render_template, url_for, session, flash
from core.models import db, User, SystemSetting
from werkzeug.security import check_password_hash

shared_routes = Blueprint('shared_routes', __name__)

@shared_routes.route('/login', methods=['GET', 'POST'])
def login():
    settings = SystemSetting.query.first()

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['role'] = user.role.lower()

            if user.role.lower() == 'admin':
                return redirect(url_for('admin_routes.admin_dashboard'))
            elif user.role.lower() == 'sales_clerk':
                return redirect(url_for('sales_routes.sales_dashboard'))
            else:
                flash("Unknown role. Contact system administrator.", "error")
                return redirect(url_for('shared_routes.login'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('shared_routes.login'))

    return render_template('home/landing.html', settings=settings)