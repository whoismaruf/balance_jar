@echo off
REM Simple deployment script for Windows
REM For production, refer to DEPLOYMENT.md

echo 🚀 Starting deployment process...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  Creating sample .env file...
    (
        echo SECRET_KEY=django-insecure-sample-key-change-in-production
        echo DEBUG=True
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo DATABASE_URL=sqlite:///db.sqlite3
    ) > .env
    echo ✅ Created .env file. Please update it with your settings.
)

REM Run migrations
echo 🗄️  Running database migrations...
python manage.py migrate

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

echo ✅ Deployment completed successfully!
echo.
echo 🎯 Next steps:
echo    1. Create a superuser: python manage.py createsuperuser
echo    2. Start development server: python manage.py runserver
echo    3. For production deployment, see DEPLOYMENT.md
echo.
pause