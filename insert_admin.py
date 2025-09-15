from core.models import db, User
from flask import Flask
from core.config import Config
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    hashed_password = generate_password_hash("sejj78ug")
    admin = User(
        username="Sejjusa",
        email="sejjtechnologies@gmail.com",
        password_hash=hashed_password,
        role="admin",
        profile_image=None  # or default filename
    )
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user inserted.")