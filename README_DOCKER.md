# Balance Jar - Docker Deployment Guide

## 🐳 Docker Setup

This guide will help you deploy the Balance Jar application using Docker with Gunicorn and an external PostgreSQL database.

### Prerequisites

- Docker and Docker Compose installed
- External PostgreSQL database (can be hosted on cloud services like AWS RDS, Digital Ocean, etc.)
- Basic knowledge of environment variables

### 📁 Project Structure

```
balance_jar/
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Service orchestration
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Template for environment variables
├── .dockerignore          # Files to exclude from Docker build
├── requirements.txt       # Python dependencies
├── deploy.sh             # Unix deployment script
├── deploy.bat            # Windows deployment script
└── README_DOCKER.md      # This file
```

### 🚀 Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd balance_jar
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your actual values (see configuration section below).

3. **Deploy using the script:**
   ```bash
   # On Unix/Linux/macOS
   chmod +x deploy.sh
   ./deploy.sh
   
   # On Windows
   deploy.bat
   ```

4. **Access the application:**
   Open http://localhost:8000 in your browser.

### ⚙️ Configuration

#### Required Environment Variables

Edit your `.env` file with these essential settings:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-immediately
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database (Choose Option 1 OR Option 2)
# Option 1: Full DATABASE_URL (Recommended)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Option 2: Individual settings
DB_NAME=balance_jar_db
DB_USER=balance_jar_user
DB_PASSWORD=your-strong-password
DB_HOST=your-postgres-host.com
DB_PORT=5432
```

#### Security Settings (Production)

For production deployment with HTTPS:

```env
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 🗄️ Database Setup

#### Option 1: Cloud PostgreSQL (Recommended)

Use services like:
- **AWS RDS**
- **Digital Ocean Managed Databases**
- **Google Cloud SQL**
- **Azure Database for PostgreSQL**
- **Supabase**
- **Neon**

#### Option 2: Self-hosted PostgreSQL

If you have your own PostgreSQL server, ensure it's accessible from your Docker containers.

### 📋 Manual Commands

#### Build and Run Manually

```bash
# Build the image
docker-compose build

# Run migrations
docker-compose run --rm migration

# Collect static files
docker-compose run --rm web python manage.py collectstatic --noinput

# Start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

#### Database Operations

```bash
# Create superuser
docker-compose run --rm web python manage.py createsuperuser

# Run custom Django commands
docker-compose run --rm web python manage.py <command>

# Access Django shell
docker-compose run --rm web python manage.py shell

# Run database migrations manually
docker-compose run --rm web python manage.py migrate
```

### 🔧 Docker Services

#### Web Service
- **Image**: Custom Django application with Gunicorn
- **Port**: 8000
- **Environment**: Loads from `.env` file
- **Volumes**: Static files and media files
- **Command**: `gunicorn --bind 0.0.0.0:8000 --workers 3 www.wsgi:application`

#### Migration Service
- **Purpose**: Runs database migrations before web service starts
- **Command**: `python manage.py migrate`
- **Restart**: No (runs once)

### 📊 Monitoring and Maintenance

#### View Application Logs
```bash
docker-compose logs -f web
```

#### Monitor Resource Usage
```bash
docker stats
```

#### Health Check
The Dockerfile includes a health check that monitors the application status.

#### Backup Considerations
- **Database**: Use your PostgreSQL provider's backup features
- **Media Files**: Volume `media_volume` should be backed up
- **Static Files**: Can be regenerated with `collectstatic`

### 🔒 Security Considerations

1. **Secret Key**: Generate a strong, unique secret key
2. **Database Password**: Use a strong password for your database
3. **HTTPS**: Enable SSL redirect in production
4. **Allowed Hosts**: Restrict to your actual domain(s)
5. **Environment File**: Never commit `.env` to version control

### 🐛 Troubleshooting

#### Common Issues

1. **Database Connection Failed**
   - Check your DATABASE_URL or individual DB settings
   - Ensure PostgreSQL server is accessible
   - Verify firewall rules

2. **Static Files Not Loading**
   - Run: `docker-compose run --rm web python manage.py collectstatic --noinput`
   - Check STATIC_ROOT and STATIC_URL settings

3. **Permission Denied**
   - Ensure Docker has necessary permissions
   - Check file ownership and permissions

4. **Port Already in Use**
   - Change the port in docker-compose.yml: `"8001:8000"`
   - Stop other services using port 8000

#### Debug Mode

To run in debug mode:
1. Set `DEBUG=True` in `.env`
2. Restart services: `docker-compose restart web`

### 🔄 Updates and Maintenance

#### Updating the Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run any new migrations
docker-compose run --rm migration
```

#### Scaling (Production)
```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3
```

### 🌐 Production Deployment

For production deployment:

1. Use a reverse proxy (Nginx/Traefik)
2. Set up SSL certificates
3. Configure proper logging
4. Set up monitoring (health checks)
5. Use Docker Swarm or Kubernetes for orchestration
6. Implement proper backup strategies

### 📞 Support

For issues specific to Docker deployment, check:
- Docker logs: `docker-compose logs`
- Container status: `docker-compose ps`
- Resource usage: `docker stats`

For application-specific issues, refer to the main project documentation.