from core.models import db, User
from flask import Flask
from core.config import Config
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    hashed_password = generate_password_hash("sejj78ug")
    clerk = User(
        username="Anonymous Tech",
        email="kato@gmail.com",
        password_hash=hashed_password,
        role="sales_clerk",
        profile_image=None  # Will be updated later
    )
    db.session.add(clerk)
    db.session.commit()
    print("✅ Sales Clerk user inserted.")