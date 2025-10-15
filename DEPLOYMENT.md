# Balance Jar - Standalone Deployment Guide

This guide covers deploying the Balance Jar Django application using Gunicorn without Docker containers.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Static Files Configuration](#static-files-configuration)
- [Process Management](#process-management)
- [Nginx Configuration](#nginx-configuration)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.11+ installed
- Git
- PostgreSQL (for production) or SQLite (for development)
- Nginx (for production reverse proxy)
- Supervisor or systemd (for process management)

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/whoismaruf/balance_jar.git
cd balance_jar
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 8. Start Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Production Deployment

### 1. Server Setup
Update your system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

Install required packages:
```bash
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git -y
```

### 2. Create Application User
```bash
sudo adduser balance_jar
sudo usermod -aG sudo balance_jar
su - balance_jar
```

### 3. Clone and Setup Application
```bash
cd /home/balance_jar
git clone https://github.com/whoismaruf/balance_jar.git
cd balance_jar
```

### 4. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Environment Configuration
Create `/home/balance_jar/balance_jar/.env`:
```env
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
DATABASE_URL=postgresql://username:password@localhost:5432/balance_jar_db
STATIC_ROOT=/home/balance_jar/balance_jar/staticfiles
MEDIA_ROOT=/home/balance_jar/balance_jar/media
```

### 6. Generate Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Database Setup

### PostgreSQL Setup (Production)

1. **Install and Configure PostgreSQL**:
```bash
sudo -u postgres psql
```

2. **Create Database and User**:
```sql
CREATE DATABASE balance_jar_db;
CREATE USER balance_jar_user WITH PASSWORD 'your-secure-password';
ALTER ROLE balance_jar_user SET client_encoding TO 'utf8';
ALTER ROLE balance_jar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE balance_jar_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE balance_jar_db TO balance_jar_user;
\q
```

3. **Update .env file**:
```env
DATABASE_URL=postgresql://balance_jar_user:your-secure-password@localhost:5432/balance_jar_db
```

### SQLite Setup (Development/Small Production)
For smaller deployments, you can continue using SQLite:
```env
DATABASE_URL=sqlite:///db.sqlite3
```

## Static Files Configuration

### 1. Run Django Commands
```bash
cd /home/balance_jar/balance_jar
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 2. Set Proper Permissions
```bash
sudo chown -R balance_jar:balance_jar /home/balance_jar/balance_jar
sudo chmod -R 755 /home/balance_jar/balance_jar
```

## Process Management

### Option 1: Using Supervisor (Recommended)

1. **Create Supervisor Configuration**:
```bash
sudo nano /etc/supervisor/conf.d/balance_jar.conf
```

Add this content:
```ini
[program:balance_jar]
command=/home/balance_jar/balance_jar/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 www.wsgi:application
directory=/home/balance_jar/balance_jar
user=balance_jar
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/balance_jar/gunicorn.log
stderr_logfile=/var/log/balance_jar/gunicorn_error.log
```

2. **Create Log Directory**:
```bash
sudo mkdir -p /var/log/balance_jar
sudo chown balance_jar:balance_jar /var/log/balance_jar
```

3. **Start the Service**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start balance_jar
```

### Option 2: Using Systemd

1. **Create Service File**:
```bash
sudo nano /etc/systemd/system/balance_jar.service
```

Add this content:
```ini
[Unit]
Description=Balance Jar Django App
After=network.target

[Service]
User=balance_jar
Group=balance_jar
WorkingDirectory=/home/balance_jar/balance_jar
Environment=PATH=/home/balance_jar/balance_jar/venv/bin
EnvironmentFile=/home/balance_jar/balance_jar/.env
ExecStart=/home/balance_jar/balance_jar/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 www.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **Enable and Start Service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable balance_jar
sudo systemctl start balance_jar
```

## Nginx Configuration

### 1. Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/balance_jar
```

Add this content:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/balance_jar/balance_jar;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        root /home/balance_jar/balance_jar;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/balance_jar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/HTTPS Setup

### Using Let's Encrypt (Recommended)

1. **Install Certbot**:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

2. **Obtain SSL Certificate**:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-renewal**:
```bash
sudo systemctl enable certbot.timer
```

## Monitoring and Logging

### 1. Application Logs
```bash
# Supervisor logs
sudo tail -f /var/log/balance_jar/gunicorn.log
sudo tail -f /var/log/balance_jar/gunicorn_error.log

# Systemd logs
sudo journalctl -u balance_jar -f
```

### 2. Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. Django Logs
Add to your Django settings for production logging:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/balance_jar/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Deployment Script

Create a deployment script `/home/balance_jar/deploy.sh`:
```bash
#!/bin/bash
set -e

echo "Starting deployment..."

# Navigate to project directory
cd /home/balance_jar/balance_jar

# Activate virtual environment
source venv/bin/activate

# Pull latest changes
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo supervisorctl restart balance_jar
# OR for systemd: sudo systemctl restart balance_jar

# Restart nginx
sudo systemctl reload nginx

echo "Deployment completed successfully!"
```

Make it executable:
```bash
chmod +x /home/balance_jar/deploy.sh
```

## Backup Strategy

### 1. Database Backup Script
Create `/home/balance_jar/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/balance_jar/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# For PostgreSQL
pg_dump balance_jar_db > $BACKUP_DIR/balance_jar_$DATE.sql

# For SQLite
# cp /home/balance_jar/balance_jar/db.sqlite3 $BACKUP_DIR/balance_jar_$DATE.sqlite3

# Keep only last 7 days of backups
find $BACKUP_DIR -name "balance_jar_*.sql" -mtime +7 -delete
```

### 2. Cron Job for Automatic Backups
```bash
crontab -e
```

Add:
```bash
# Daily database backup at 2 AM
0 2 * * * /home/balance_jar/backup_db.sh
```

## Troubleshooting

### Common Issues

1. **500 Internal Server Error**:
   - Check Django logs: `/var/log/balance_jar/django.log`
   - Verify environment variables in `.env`
   - Ensure all migrations are applied

2. **Static Files Not Loading**:
   - Run `python manage.py collectstatic --noinput`
   - Check Nginx configuration for static file paths
   - Verify file permissions

3. **Database Connection Issues**:
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env`
   - Test connection: `psql -h localhost -U balance_jar_user -d balance_jar_db`

4. **Application Won't Start**:
   - Check Gunicorn logs
   - Verify Python virtual environment is activated
   - Ensure all dependencies are installed

### Performance Tuning

1. **Gunicorn Workers**:
   - Formula: `(2 * CPU cores) + 1`
   - Monitor CPU/Memory usage and adjust accordingly

2. **Database Optimization**:
   - Add database indexes for frequently queried fields
   - Use database connection pooling
   - Configure PostgreSQL for your hardware

3. **Caching**:
   - Install Redis: `sudo apt install redis-server`
   - Add Redis caching to Django settings

### Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] ALLOWED_HOSTS properly configured
- [ ] SSL/HTTPS enabled
- [ ] Regular security updates
- [ ] Database backups
- [ ] Firewall configured
- [ ] Regular log monitoring

## Cloud Deployment Options

### Railway
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Railway will automatically build and deploy

### Heroku
1. Install Heroku CLI
2. Create `Procfile`: `web: gunicorn www.wsgi:application`
3. Deploy: `git push heroku main`

### DigitalOcean App Platform
1. Connect repository
2. Configure build and run commands
3. Set environment variables

---

For support, please check the project documentation or open an issue on GitHub.