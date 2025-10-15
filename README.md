# Balance Jar 💰

A Django web application for managing personal finances with jar-based budgeting.

## Features

- 👤 User authentication and profiles
- 🏦 Account management
- 🫙 Jar-based budgeting system
- 💸 Transaction tracking (Income, Expenses, Transfers)
- 📱 Responsive mobile-friendly interface
- 🔄 Transfer money between jars and accounts

## Quick Start

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/whoismaruf/balance_jar.git
   cd balance_jar
   ```

2. **Run the deployment script**:
   ```bash
   # On Linux/Mac
   chmod +x deploy.sh
   ./deploy.sh
   
   # On Windows
   deploy.bat
   ```

3. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:8000`

### Manual Setup

If you prefer manual setup:

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   ```

4. **Run migrations and collect static files**:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

## Production Deployment

For production deployment instructions (including Gunicorn, Nginx, SSL, and cloud deployments), see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## Technology Stack

- **Backend**: Django 5.2.7, Python 3.11+
- **Frontend**: Bootstrap 5, Django Templates
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django Allauth
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Deployment**: Gunicorn, Nginx, Supervisor/systemd

## Project Structure

```
balance_jar/
├── core/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL routing
│   └── templates/         # HTML templates
├── www/                   # Django project settings
│   ├── settings.py        # Configuration
│   └── urls.py           # Root URL patterns
├── templates/             # Global templates
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── deploy.sh             # Deployment script (Linux/Mac)
├── deploy.bat            # Deployment script (Windows)
└── DEPLOYMENT.md         # Production deployment guide
```

## Key Features

### Jar-Based Budgeting
- Create multiple savings jars for different goals
- Allocate money to specific purposes
- Track progress towards financial goals

### Transaction Management
- Record income and expenses
- Transfer money between jars
- Cross-account transfers
- Detailed transaction history

### User-Friendly Interface
- Responsive design works on desktop and mobile
- Intuitive navigation
- Clear transaction forms with helpful guidance

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## Support

- 📖 Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- 🐛 Open an issue for bug reports
- 💡 Submit feature requests via GitHub issues

## License

This project is open source and available under the [MIT License](LICENSE).

---

Built with ❤️ using Django