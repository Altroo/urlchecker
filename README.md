# 🌐 URL Health Monitor
A Django-based web application for monitoring the health and availability of URLs/websites in real-time. Features a modern Semantic UI dashboard, REST API, and asynchronous health checking with Celery.
## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [AWS EC2 Deployment](#aws-ec2-deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

## ✨ Features
- **Real-time URL monitoring** with health status tracking
- **REST API** for programmatic access
- **Modern web dashboard** with Semantic UI
- **Asynchronous task processing** using Celery
- **Responsive design** for mobile and desktop
- **Health check history** with detailed metrics
- **Auto-refresh dashboard** with live updates
- **Manual health checks** on demand

## 🏗️ Architecture
``` 
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django Web    │    │     Redis       │    │   Celery Worker │
│   Application   │◄──►│   Message       │◄──►│   Background    │
│   (REST API +   │    │   Broker        │    │   Tasks         │
│   Dashboard)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sqlite        │    │   Task Queue    │    │   HTTP Requests │
│   Database      │    │   Management    │    │   to Target     │
│   (URLs +       │    │                 │    │   URLs          │
│   Health Data)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
### Key Components:
- **Django**: Web framework handling HTTP requests, REST API, and dashboard
- **Sqlite**: Primary database for storing URLs and health check data
- **Redis**: Message broker for Celery task queue and caching
- **Celery**: Asynchronous task processor for health checks
- **Semantic UI**: Frontend framework for modern, responsive UI

## 📦 Prerequisites
- Python 3.12+
- Redis 6+
- Git

## 🚀 Local Development Setup
### 1. Clone the Repository
``` bash
git clone <repository-url>
cd url-health-monitor
```
### 2. Set Up Python Environment
``` bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Redis Setup
``` bash
# Install Redis or use Docker
docker run --name redis-urlmonitor -p 6379:6379 -d redis:7-alpine
```
### 4. Environment Configuration
Create `.env` file in the project root:
``` bash
# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```
### 6. Run Migrations
``` bash
python manage.py makemigrations
python manage.py migrate
```
### 7. Create Superuser (Optional)
``` bash
python manage.py createsuperuser
```
### 8. Start Services
**Terminal 1 - Django Development Server:**
``` bash
python manage.py runserver
```
**Terminal 2 - Celery Worker:**
``` bash
celery -A urlchecker worker --loglevel=info
```
**Terminal 3 - Celery Beat (Optional - for periodic tasks):**
``` bash
celery -A urlchecker beat --loglevel=info
```
### 9. Access the Application
- **Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **API Root**: [http://localhost:8000/api/](http://localhost:8000/api/)
- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## ☁️ AWS EC2 Deployment
### 1. Launch EC2 Instance
- **Instance Type**: t3.small or larger
- **OS**: Ubuntu 22.04 LTS
- **Security Groups**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

### 2. Connect and Update System
``` bash
ssh -i your-key.pem ubuntu@your-ec2-ip

sudo apt update && sudo apt upgrade -y
```
### 3. Install Dependencies
``` bash
# Python and Redis
sudo apt install -y python3-pip python3-venv nginx redis-server

# Start services
sudo systemctl start redis-server nginx
sudo systemctl enable redis-server nginx
```
### 4. Application Setup
``` bash
# Clone repository
git clone <repository-url> /opt/urlmonitor
cd /opt/urlmonitor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 5. Production Environment Configuration
Create `/opt/urlmonitor/.env`:
``` bash
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip
```
### 6. Run Migrations and Collect Static Files
``` bash
python manage.py migrate
python manage.py collectstatic --noinput
```
### 7. Create Systemd Services
**Django Service** (`/etc/systemd/system/urlmonitor.service`):
``` ini
[Unit]
Description=URL Monitor Django App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/urlmonitor
Environment=PATH=/opt/urlmonitor/venv/bin
ExecStart=/opt/urlmonitor/venv/bin/gunicorn --bind 127.0.0.1:8000 urlchecker.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```
**Celery Worker Service** (`/etc/systemd/system/urlmonitor-celery.service`):
``` ini
[Unit]
Description=URL Monitor Celery Worker
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/urlmonitor
Environment=PATH=/opt/urlmonitor/venv/bin
ExecStart=/opt/urlmonitor/venv/bin/celery -A urlchecker worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```
### 8. Configure Nginx
Create `/etc/nginx/sites-available/urlmonitor`:
``` nginx
server {
    listen 80;
    server_name your-domain.com your-ec2-ip;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/urlmonitor/staticfiles/;
    }
}
```
### 9. Enable and Start Services
``` bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/urlmonitor /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Start all services
sudo systemctl daemon-reload
sudo systemctl enable urlmonitor urlmonitor-celery
sudo systemctl start urlmonitor urlmonitor-celery nginx

# Restart Nginx
sudo systemctl restart nginx
```
## 📚 API Documentation
### Base URL
``` 
http://your-domain.com/api/
```
### Authentication
Currently, the API does not require authentication. For production use, consider implementing Django REST framework authentication.
### Endpoints
#### 1. Add New URL to Monitor
``` http
POST /api/urls/
Content-Type: application/json

{
    "name": "Google",
    "url": "https://google.com",
    "is_active": true
}
```
**Response:**
``` json
{
    "id": 1,
    "name": "Google",
    "url": "https://google.com",
    "created_at": "2025-01-01T12:00:00Z",
    "is_active": true,
    "latest_health_check": null,
    "status_display": "Unknown"
}
```
#### 2. List All Monitored URLs
``` http
GET /api/urls/
```
**Response:**
``` json
[
    {
        "id": 1,
        "name": "Google",
        "url": "https://google.com",
        "created_at": "2025-01-01T12:00:00Z",
        "is_active": true,
        "latest_health_check": {
            "id": 1,
            "status_code": 200,
            "response_time": 0.245,
            "checked_at": "2025-01-01T12:05:00Z",
            "is_healthy": true,
            "error_message": null
        },
        "status_display": "Healthy"
    }
]
```
#### 3. Get URL Details with Latest Status
``` http
GET /api/urls/{id}/
```
**Response:**
``` json
{
    "id": 1,
    "name": "Google",
    "url": "https://google.com",
    "created_at": "2025-01-01T12:00:00Z",
    "is_active": true,
    "latest_health_check": {
        "id": 1,
        "status_code": 200,
        "response_time": 0.245,
        "checked_at": "2025-01-01T12:05:00Z",
        "is_healthy": true,
        "error_message": null
    },
    "status_display": "Healthy"
}
```
#### 4. Delete URL from Monitoring
``` http
DELETE /api/urls/{id}/
```
**Response:**
``` json
{
    "message": "URL \"Google\" has been removed from monitoring.",
    "status": "deleted"
}
```
#### 5. Get Health Check History
``` http
GET /api/urls/{id}/history/
GET /api/urls/{id}/history/?limit=100
```
**Response:**
``` json
{
    "url_id": 1,
    "url_name": "Google",
    "total_checks": 10,
    "history": [
        {
            "id": 10,
            "status_code": 200,
            "response_time": 0.234,
            "checked_at": "2025-01-01T12:05:00Z",
            "is_healthy": true,
            "error_message": null
        },
        {
            "id": 9,
            "status_code": 200,
            "response_time": 0.287,
            "checked_at": "2025-01-01T12:00:00Z",
            "is_healthy": true,
            "error_message": null
        }
    ]
}
```
#### 6. Trigger Immediate Health Check
``` http
POST /api/urls/{id}/check-now/
```
**Response:**
``` json
{
    "message": "Health check queued for Google",
    "url_id": 1,
    "url_name": "Google",
    "task_id": "celery-task-id-here",
    "status": "queued"
}
```
## 📁 Project Structure
``` 
url-health-monitor/
├── urlchecker/             # Django project settings
│   ├── __init__.py
│   ├── settings.py         # Django configuration
│   ├── urls.py             # Main URL routing
│   ├── asgi.py             # ASGI application
│   ├── wsgi.py             # WSGI application
│   └── celery.py           # Celery configuration
├── monitor/                # Django app
│   ├── __init__.py
│   ├── models.py           # URL and HealthCheck models
│   ├── views.py            # API views and dashboard
│   ├── serializers.py      # DRF serializers
│   ├── tasks.py            # Celery tasks
│   ├── urls.py             # App URL routing
│   ├── migrations/         # Database migrations
│   ├── static/             # Static files (CSS, JS)
│   │   ├── css/
│   │   │   └── dashboard.css
│   │   └── js/
│   │       └── monitor-dashboard.js
│   ├───tests/
│   │   └── __init__.py
│   │   └── test_models.py  # Unit test for models
│   │   └── test_tasks.py   # Unit test for tasks
│   │   └── test_views.py   # Unit test for views
│   └── templates/          # HTML templates
│       └── dashboard.html
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
├── Dockerfile             # Docker configuration
└── README.md              # This file
```
## ⚙️ Configuration
### Environment Variables

| Variable | Description                           | Default |
| --- |---------------------------------------| --- |
| `DATABASE_URL` | Sqlite connection string              | Required |
| `REDIS_URL` | Redis connection string               | Required |
| `SECRET_KEY` | Django secret key                     | Required |
| `DEBUG` | Django debug mode                     | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Required |
| `CELERY_BROKER_URL` | Celery broker URL                     | Same as `REDIS_URL` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL             | Same as `REDIS_URL` |
### Django Settings
Key settings in `urlchecker/settings.py`:
- **Database**: Sqlite with connection pooling
- **Cache**: Redis for session and cache storage
- **Static Files**: Configured for production deployment
- **CORS**: Enabled for API access
- **REST Framework**: Configured with pagination

### Logs
**View application logs:**
``` bash
# Django logs
sudo journalctl -u urlmonitor -f

# Celery logs  
sudo journalctl -u urlmonitor-celery -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```
### Health Checks
**Verify services:**
``` bash
# Check Django
curl http://localhost:8000/api/urls/

# Check Redis
redis-cli ping

# Check Celery
celery -A urlchecker inspect ping
```

