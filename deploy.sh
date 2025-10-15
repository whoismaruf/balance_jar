#!/bin/bash

# Simple deployment script for local/development use
# For production, refer to DEPLOYMENT.md

set -e

echo "🚀 Starting deployment process..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Creating sample .env file..."
    cat > .env << EOF
SECRET_KEY=django-insecure-sample-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EOF
    echo "✅ Created .env file. Please update it with your settings."
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "   1. Create a superuser: python manage.py createsuperuser"
echo "   2. Start development server: python manage.py runserver"
echo "   3. For production deployment, see DEPLOYMENT.md"
echo ""