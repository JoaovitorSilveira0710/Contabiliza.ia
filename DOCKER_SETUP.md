# 🐳 Docker Setup Guide

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build
```

### 2. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/
- **Django Admin**: http://localhost/admin/
- **Direct Backend**: http://localhost:8000

### 3. Create Superuser

```bash
docker-compose exec web python django_backend/manage.py createsuperuser
```

## Services

The docker-compose setup includes:

1. **web** - Django application (port 8000)
2. **db** - PostgreSQL database (port 5432)
3. **nginx** - Reverse proxy and static file server (port 80)

## Useful Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Stop Services
```bash
docker-compose down

# Remove volumes (deletes database data)
docker-compose down -v
```

### Run Django Commands
```bash
# Migrations
docker-compose exec web python django_backend/manage.py makemigrations
docker-compose exec web python django_backend/manage.py migrate

# Shell
docker-compose exec web python django_backend/manage.py shell

# Backup database
docker-compose exec web python django_backend/manage.py backup_database
```

### Database Access
```bash
# PostgreSQL shell
docker-compose exec db psql -U contabiliza_user -d contabiliza
```

## Production Deployment

### 1. Update Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
DEBUG=0
SECRET_KEY=your-secure-random-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Use Production Settings

Update `docker-compose.yml` for production:

```yaml
environment:
  - DEBUG=0
  - SECRET_KEY=${SECRET_KEY}
  - ALLOWED_HOSTS=${ALLOWED_HOSTS}
```

### 3. Collect Static Files

```bash
docker-compose exec web python django_backend/manage.py collectstatic --noinput
```

## GitHub Deployment

### Push to GitHub

```bash
git add .
git commit -m "Add Docker configuration"
git push origin main
```

### Deploy on Server

```bash
# Clone repository
git clone https://github.com/JoaovitorSilveira0710/Contabiliza.ia.git
cd Contabiliza.ia

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Build and run
docker-compose up -d --build

# Create superuser
docker-compose exec web python django_backend/manage.py createsuperuser
```

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
ports:
  - "8080:8000"  # Instead of 8000:8000
```

### Database Connection Issues

```bash
# Restart database service
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Permission Issues

```bash
# Fix permissions on storage/backups folders
docker-compose exec web chmod -R 755 storage backups
```

## Development vs Production

**Development** (current setup):
- SQLite database (optional)
- DEBUG=1
- Hot reload enabled
- Volume mounting for live code changes

**Production** (recommended):
- PostgreSQL database
- DEBUG=0
- Static files collected
- Proper SECRET_KEY
- SSL/HTTPS configured
- Environment variables from .env file
