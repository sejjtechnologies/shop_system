@echo off
title Shop System Installer
echo 🛠️ Setting up your Shop System...
echo.

:: Create virtual environment if missing
if not exist venv (
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install dependencies
echo 📦 Installing Python packages...
pip install -r requirements.txt

:: Apply database migrations
echo 🧱 Applying database migrations...
flask db upgrade

:: Seed permissions and roles
echo 🔐 Seeding permissions and role mappings...
python seed_permissions.py
python seed_role_permissions.py

:: Insert default admin user
echo 👤 Creating default admin account...
python insert_admin.py

:: Launch the system
echo.
echo 🚀 Launching Shop System...
start http://127.0.0.1:5000
python app.py

pause