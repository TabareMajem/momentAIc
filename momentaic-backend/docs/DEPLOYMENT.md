# Momentaic Deployment Guide - Hostinger VPS

Complete guide for deploying Momentaic to momentaic.com on Hostinger VPS.

## Prerequisites

- Hostinger VPS with Ubuntu 22.04+
- Docker and Docker Compose installed
- Domain `momentaic.com` pointing to VPS IP
- Subdomain `api.momentaic.com` pointing to same VPS IP

## Quick Start

### 1. Connect to VPS

```bash
ssh root@your-vps-ip
```

### 2. Install Docker (if not installed)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 3. Clone Repository

```bash
mkdir -p /opt/momentaic
cd /opt/momentaic
git clone https://github.com/yourusername/momentaic.git .
```

### 4. Configure Environment

```bash
cd momentaic-backend
cp .env.production.template .env

# Edit with your actual values
nano .env
```

**Required values to change:**
- `SECRET_KEY` - Generate: `openssl rand -hex 32`
- `JWT_SECRET_KEY` - Generate: `openssl rand -hex 32`
- `POSTGRES_PASSWORD` - Strong password
- `GOOGLE_API_KEY` - From Google AI Studio
- `STRIPE_SECRET_KEY` - From Stripe Dashboard

### 5. Create Database Init Script

```bash
cat > scripts/init-db.sql << 'EOF'
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
SET timezone = 'UTC';
EOF
```

### 6. Start Services

```bash
# Build and start all containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 7. Run Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 8. Set Up Nginx (Host Level)

```bash
# Install Nginx
sudo apt install nginx -y

# Copy config
sudo cp nginx/momentaic.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/momentaic.conf /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### 9. Set Up SSL with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificates
sudo certbot --nginx -d momentaic.com -d www.momentaic.com -d api.momentaic.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Port Summary

| Service | Internal Port | External Port |
|---------|---------------|---------------|
| Frontend | 80 | 2685 |
| Backend API | 8000 | 2682 |
| PostgreSQL | 5432 | - (internal only) |
| Redis | 6379 | - (internal only) |

Nginx proxies to these ports from 80/443.

## Verification

### Health Checks

```bash
# Backend health
curl http://localhost:2682/api/v1/health

# Frontend health
curl http://localhost:2685/health
```

### Full Stack Test

1. Open https://momentaic.com in browser
2. Click "Get Started" 
3. Complete signup flow
4. Verify you reach the dashboard

## Troubleshooting

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
```

### Restart Services

```bash
docker-compose restart api
```

### Rebuild After Changes

```bash
docker-compose up -d --build api
```

### Database Issues

```bash
# Connect to database
docker-compose exec postgres psql -U momentaic -d momentaic

# Check migrations
docker-compose exec api alembic current
```

## Backup

### Database Backup

```bash
docker-compose exec postgres pg_dump -U momentaic momentaic > backup_$(date +%Y%m%d).sql
```

### Full Backup

```bash
tar -czf momentaic_backup_$(date +%Y%m%d).tar.gz \
    .env \
    uploads/ \
    logs/
```

## Updates

```bash
cd /opt/momentaic
git pull origin main
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker-compose exec api alembic upgrade head
```
