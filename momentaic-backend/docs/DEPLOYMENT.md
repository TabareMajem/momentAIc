# MomentAIc Production Deployment Guide

This guide covers deploying MomentAIc to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Deployment Options](#deployment-options)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Scaling](#scaling)
8. [Backup & Recovery](#backup--recovery)
9. [Security Hardening](#security-hardening)

---

## Prerequisites

### Required Services

- **PostgreSQL 16+** with pgvector extension
- **Redis 7+** for caching and Celery
- **Domain** with DNS configured
- **SSL Certificate** (Let's Encrypt recommended)

### Minimum System Requirements

| Component | CPU | RAM | Storage |
|-----------|-----|-----|---------|
| API Server | 2 cores | 4 GB | 20 GB |
| Database | 2 cores | 8 GB | 100 GB SSD |
| Redis | 1 core | 2 GB | 10 GB |
| Celery Worker | 2 cores | 4 GB | 20 GB |

---

## Environment Configuration

### Required Environment Variables

```bash
# Application
APP_ENV=production
APP_NAME=MomentAIc
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/momentaic
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis-host:6379/0
CELERY_BROKER_URL=redis://redis-host:6379/1
CELERY_RESULT_BACKEND=redis://redis-host:6379/2

# Security
JWT_SECRET_KEY=<generate-256-bit-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["https://app.momentaic.com","https://momentaic.com"]

# AI Providers
GOOGLE_API_KEY=<your-gemini-api-key>
ANTHROPIC_API_KEY=<your-anthropic-key>  # Optional

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_STARTER_PRICE_ID=price_xxx
STRIPE_GROWTH_PRICE_ID=price_xxx
STRIPE_GOD_MODE_PRICE_ID=price_xxx

# Email (SMTP)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@momentaic.com
FROM_NAME=MomentAIc

# External APIs
SERPER_API_KEY=<serper-key>
TAVILY_API_KEY=<tavily-key>
```

### Generate Secure Keys

```bash
# Generate JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate webhook secrets
python -c "import secrets; print('wh_' + secrets.token_urlsafe(32))"
```

---

## Database Setup

### PostgreSQL with pgvector

```sql
-- Create database
CREATE DATABASE momentaic;

-- Connect to database
\c momentaic

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create application user
CREATE USER momentaic_app WITH PASSWORD '<strong-password>';
GRANT ALL PRIVILEGES ON DATABASE momentaic TO momentaic_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO momentaic_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO momentaic_app;
```

### Run Migrations

```bash
# From production server or CI/CD
alembic upgrade head
```

---

## Deployment Options

### Option 1: Docker Compose (Simple)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: momentaic:latest
    restart: always
    environment:
      - APP_ENV=production
    env_file:
      - .env.production
    ports:
      - "8000:8000"
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G

  celery-worker:
    image: momentaic:latest
    restart: always
    command: celery -A app.tasks.celery_app worker --loglevel=info
    env_file:
      - .env.production
    deploy:
      replicas: 2

  celery-beat:
    image: momentaic:latest
    restart: always
    command: celery -A app.tasks.celery_app beat --loglevel=info
    env_file:
      - .env.production

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
```

### Option 2: Kubernetes

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: momentaic-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: momentaic-api
  template:
    metadata:
      labels:
        app: momentaic-api
    spec:
      containers:
      - name: api
        image: ghcr.io/yourorg/momentaic:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: momentaic-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Option 3: Railway/Render/Fly.io

These platforms support automatic deployment from GitHub:

1. Connect your repository
2. Set environment variables in dashboard
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## SSL/TLS Configuration

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/momentaic
upstream momentaic {
    server 127.0.0.1:8000;
    keepalive 64;
}

server {
    listen 80;
    server_name api.momentaic.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.momentaic.com;

    ssl_certificate /etc/letsencrypt/live/api.momentaic.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.momentaic.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://momentaic;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /api/v1/health {
        proxy_pass http://momentaic;
        access_log off;
    }
}
```

### Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.momentaic.com

# Auto-renewal (cron)
0 0 1 * * /usr/bin/certbot renew --quiet
```

---

## Monitoring & Logging

### Application Metrics

Add Prometheus metrics endpoint:

```python
# app/main.py (add to existing)
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Log Aggregation

Configure structured logging to be collected by:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Datadog**
- **Sentry** for error tracking

```python
# Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### Health Checks

The `/api/v1/health` endpoint returns:
- Application status
- Database connectivity
- Redis connectivity
- Celery worker status

---

## Scaling

### Horizontal Scaling

1. **API Servers**: Add more replicas behind load balancer
2. **Celery Workers**: Scale based on queue depth
3. **Database**: Use read replicas for queries

### Vertical Scaling

Increase resources for:
- Database (more RAM for caching)
- Redis (more memory for sessions)
- Workers (more CPU for AI processing)

### Auto-scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: momentaic-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: momentaic-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Backup & Recovery

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/postgres

pg_dump -h localhost -U postgres momentaic | gzip > $BACKUP_DIR/momentaic_$DATE.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/momentaic_$DATE.sql.gz s3://momentaic-backups/postgres/
```

### Redis Backups

Enable RDB snapshots and AOF persistence:

```
# redis.conf
save 900 1
save 300 10
save 60 10000
appendonly yes
```

---

## Security Hardening

### Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Enable firewall (UFW/iptables)
- [ ] Disable root SSH access
- [ ] Use SSH keys only
- [ ] Keep systems updated
- [ ] Enable fail2ban
- [ ] Regular security audits
- [ ] Encrypt data at rest
- [ ] Use secrets management (Vault, AWS Secrets Manager)

### Rate Limiting

Configure based on tier:
- Starter: 60 requests/minute
- Growth: 300 requests/minute
- God Mode: 1000 requests/minute

### API Key Security

- Rotate keys regularly
- Use short-lived tokens
- Implement IP allowlisting for webhooks

---

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check connection string
   - Verify firewall rules
   - Check max_connections setting

2. **Celery Tasks Not Running**
   - Verify Redis connectivity
   - Check worker logs
   - Ensure queues match

3. **High Memory Usage**
   - Tune worker concurrency
   - Check for memory leaks
   - Increase swap space

### Useful Commands

```bash
# Check API health
curl https://api.momentaic.com/api/v1/health

# View container logs
docker logs momentaic-api -f --tail 100

# Check database connections
psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='momentaic';"

# Monitor Celery
celery -A app.tasks.celery_app inspect active
celery -A app.tasks.celery_app inspect stats
```

---

## Support

- **Documentation**: https://docs.momentaic.com
- **Status Page**: https://status.momentaic.com
- **Support Email**: support@momentaic.com
