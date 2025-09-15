from flask import Flask, render_template
from flask_migrate import Migrate
from sqlalchemy import text
from core.models import db, SystemSetting
from core.config import Config
from routes.shared_routes import shared_routes  # Central login logic
from routes.admin_routes import admin_routes
from routes.sales_routes import sales_routes

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and migration engine
db.init_app(app)
migrate = Migrate(app, db)

# Register shared login blueprint
app.register_blueprint(shared_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(sales_routes)

@app.route('/')
def landing():
    settings = SystemSetting.query.first()
    return render_template('home/landing.html', settings=settings)  # Login form lives here

# Test connection on startup
with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print("✅ Connected to PostgreSQL.")
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == '__main__':
    app.run(debug=True)