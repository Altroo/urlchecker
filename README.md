# 🌐 URL Health Monitor
A Django-based web application for monitoring the health and availability of URLs/websites in real-time. Features a modern Semantic UI dashboard, REST API, and asynchronous health checking with Celery. Deployed with Docker containers, Nginx reverse proxy, and SSL/TLS encryption.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Production Deployment](#docker-production-deployment)
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
- **Docker containerization** for easy deployment
- **SSL/TLS encryption** with Let's Encrypt
- **Nginx reverse proxy** for production

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

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Django debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | Required |
| `CELERY_BROKER_URL` | Celery broker URL | Same as `REDIS_URL` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | Same as `REDIS_URL` |


### Key Components:
- **Docker**: Containerized deployment with docker-compose
- **Nginx**: Reverse proxy, SSL termination, static file serving
- **Django + Gunicorn**: Web application with WSGI server
- **SQLite**: Primary database for storing URLs and health check data
- **Redis**: Message broker for Celery task queue and caching
- **Celery**: Asynchronous task processor for health checks
- **Let's Encrypt**: Free SSL/TLS certificates with auto-renewal
- **Semantic UI**: Frontend framework for modern, responsive UI

## 📦 Prerequisites
- Docker 20.0+
- Docker Compose 2.0+
- Git
- Domain name (for SSL setup)

## 🚀 Local Development Setup
### 1. Clone the Repository
```
git clone <repository-url>
cd url-health-monitor
```
### 2. Environment Configuration
Create `.env` file in the project root:
```
# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://redis:6379/0

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```
### 3. Build and Run with Docker
```
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up --build -d
```
### 4. Initialize Database
# Run migrations
```
docker-compose exec web python manage.py migrate
```
# Create superuser (optional)
```
docker-compose exec web python manage.py createsuperuser
```
# Collect static files
```
docker-compose exec web python manage.py collectstatic --noinput
```
### 5. Access the Application
```
- **Dashboard**: [http://localhost:8000/](http://localhost:8000/)
- **API Root**: [http://localhost:8000/api/](http://localhost:8000/api/)
- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
```
## ☁️ Docker Production Deployment
### 1. Server Setup
```
Launch a cloud server (AWS EC2, DigitalOcean, etc.) with:
- **OS**: Ubuntu 22.04 LTS or similar
- **RAM**: 2GB minimum
- **Storage**: 20GB minimum
- **Ports**: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```
### 2. Install Docker
```
# Update system
```
sudo apt update && sudo apt upgrade -y
```
# Install Docker
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

# Install Docker Compose
```
sudo apt install docker-compose-plugin
```
# Add user to docker group
```
sudo usermod -aG docker $USER
newgrp docker
```
### 3. Deploy Application
```

# Clone repository
```
git clone <repository-url> /opt/urlmonitor
cd /opt/urlmonitor
```
# Create production environment file
```
cp .env.example .env
```
### 4. Production Environment Configuration
Edit `.env` file:
```

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Redis
REDIS_URL=redis://redis:6379/0

# Django (Production Settings)
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-server-ip

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```
### 5. Create Docker Files
**Dockerfile**:
```
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for static
RUN mkdir -p staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "urlchecker.wsgi:application"]
```
**docker-compose.yml**:
```
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 urlchecker.wsgi:application"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    expose:
      - "8000"
    depends_on:
      - redis
    env_file:
      - .env

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"  # HTTPS port
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - ./certbot/conf:/etc/letsencrypt  # SSL certificates
      - ./certbot/www:/var/www/certbot   # Certbot challenges

    depends_on:
      - web
    command: "/bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done & nginx -g \"daemon off;\"'"

  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

  celery:
    build: .
    command: celery -A urlchecker worker --loglevel=info --pool=solo
    volumes:
      - .:/app
    depends_on:
      - redis
    env_file:
      - .env

volumes:
  static_volume:
```
### 6. Configure Nginx
**nginx.conf**:
```
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    upstream django {
        server web:8000;
    }

    # HTTP server - redirects to HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        
        # Let's Encrypt challenges
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        # Redirect all other HTTP traffic to HTTPS
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
        
        # SSL Security Settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Static files
        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
        
        # Media files
        location /media/ {
            alias /app/media/;
            expires 30d;
        }
        
        # Main application
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
    }
}
```
### 7. Setup SSL with Let's Encrypt
```
Create init-letsencrypt.sh:
```
```
#!/bin/bash

# Replace with your domain and email
domains=(your-domain.com)
rsa_key_size=4096
data_path="./certbot"
email="your-email@example.com"
staging=0 # Set to 1 if you're testing your setup

if [ -d "$data_path" ]; then
  read -p "Existing data found for $domains. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

echo "### Creating dummy certificate for $domains ..."
path="/etc/letsencrypt/live/$domains"
mkdir -p "$data_path/conf/live/$domains"
docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" certbot
echo

echo "### Starting nginx ..."
docker-compose up --force-recreate -d nginx
echo

echo "### Deleting dummy certificate for $domains ..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf" certbot
echo

echo "### Requesting Let's Encrypt certificate for $domains ..."
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload
```

### 8. Deploy with SSL
```shell script
# Make SSL script executable
chmod +x init-letsencrypt.sh

# Update configuration files with your domain and email
# Edit nginx.conf: Replace 'your-domain.com' with your actual domain
# Edit init-letsencrypt.sh: Replace domain and email

# Run initial deployment
docker-compose up --build -d

# Setup SSL certificates
./init-letsencrypt.sh

# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```


### 9. Access Your Secure Application
- **HTTPS Dashboard**: https://your-domain.com
- **API**: https://your-domain.com/api/
- **Admin**: https://your-domain.com/admin/

## 📚 API Documentation
### Base URL
```
https://your-domain.com/api/
```

### Endpoints
#### 1. Add New URL to Monitor
```
POST /api/urls/
Content-Type: application/json

{
    "name": "Google",
    "url": "https://google.com",
    "is_active": true
}
```


**Response:**
```json
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
```
GET /api/urls/
```


#### 3. Get URL Details with Latest Status
```
GET /api/urls/{id}/
```


#### 4. Delete URL from Monitoring
```
DELETE /api/urls/{id}/
```


#### 5. Get Health Check History
```
GET /api/urls/{id}/history/
GET /api/urls/{id}/history/?limit=100
```


#### 6. Trigger Immediate Health Check
```
POST /api/urls/{id}/check-now/
```

### Docker Commands
```shell script
# View logs
docker-compose logs -f web        # Django logs
docker-compose logs -f celery     # Celery logs
docker-compose logs -f nginx      # Nginx logs

# Restart services
docker-compose restart web
docker-compose restart celery
docker-compose restart nginx

# Update application
git pull
docker-compose up --build -d

# Database operations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell
```

### SSL Certificate Renewal
Certificates are automatically renewed by the certbot container. To manually renew:
```shell script
docker-compose run --rm certbot renew
docker-compose exec nginx nginx -s reload
```

### Health Checks
**Verify services:**
```shell script
# Check all containers
docker-compose ps

# Check application
curl https://your-domain.com/api/urls/

# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

## Running Tests

### Run All Tests
```bash
# Using pytest (recommended)
pytest tests/

# Using Python's unittest module
python -m unittest discover tests/

# Using Django's test runner (if Django project)
python manage.py test tests/
```

### Run Specific Test Files

```bash
# Run model tests only
pytest tests/test_models.py

# Run task tests only
pytest tests/test_tasks.py

# Run view tests only
pytest tests/test_views.py
```

### Run with Coverage Report

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html

# Generate coverage report in terminal
pytest tests/ --cov=. --cov-report=term-missing
```

### Run with Verbose Output

```bash
# See detailed test output
pytest tests/ -v

# See even more detailed output
pytest tests/ -vv
```