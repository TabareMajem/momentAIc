#!/bin/bash
# =============================================================================
# MOMENTAIC PRODUCTION DEPLOYMENT SCRIPT
# Run this on the VPS (72.62.151.245)
# =============================================================================

set -e

echo "🚀 MomentAIc Production Deployment"
echo "=================================="

# Create project directory
DEPLOY_DIR="/opt/momentaic"
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

echo "📁 Deploying to: $DEPLOY_DIR"

# Check if git repo exists, clone or pull
if [ -d ".git" ]; then
    echo "📥 Updating existing repo..."
    git pull origin main
else
    echo "📥 Cloning repository..."
    # NOTE: Replace with your actual repo URL
    git clone https://github.com/TabareMajem/momentaic.git .
fi

# Copy the production environment file
echo "⚙️ Setting up environment..."
cat > .env << 'ENVEOF'
# =============================================================================
# MOMENTAIC PRODUCTION ENVIRONMENT
# Generated: 2024-12-17
# =============================================================================

# Application
APP_NAME=MomentAIc
APP_ENV=production
DEBUG=false
SECRET_KEY=ae8f3d1c4b5e6a7f8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b
API_V1_PREFIX=/api/v1

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=2

# DATABASE (PostgreSQL)
POSTGRES_USER=momentaic
POSTGRES_PASSWORD=17122f617a04c22b1821e4344aab9f8a
POSTGRES_DB=momentaic
DATABASE_URL=postgresql+asyncpg://momentaic:17122f617a04c22b1821e4344aab9f8a@postgres:5432/momentaic
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=5

# REDIS
REDIS_PASSWORD=804698df664bf82bf2dbcf76b810115c
REDIS_URL=redis://:804698df664bf82bf2dbcf76b810115c@redis:6379/0
CELERY_BROKER_URL=redis://:804698df664bf82bf2dbcf76b810115c@redis:6379/1
CELERY_RESULT_BACKEND=redis://:804698df664bf82bf2dbcf76b810115c@redis:6379/2

# JWT AUTH
JWT_SECRET_KEY=ae8f3d1c4b5e6a7f8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI PROVIDERS (Add your keys here)
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# STRIPE (Add your keys here)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# EMAIL SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@momentaic.com
SMTP_FROM_NAME=MomentAIc

# CROSS-PLATFORM SSO
CROSS_PLATFORM_SECRET=momentaic_agentforge_sso_2024
AGENTFORGE_API_URL=https://api.agentforgeai.com

# CREDITS
DEFAULT_STARTER_CREDITS=50
DEFAULT_GROWTH_CREDITS=500
DEFAULT_GOD_MODE_CREDITS=5000

# CORS
CORS_ORIGINS=["https://momentaic.com","https://www.momentaic.com","http://localhost:2685"]

# RATE LIMITING
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
ENVEOF

echo "✅ Environment file created"

# Build and start containers
echo "🐳 Building and starting Docker containers..."
cd momentaic-backend
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec -T api alembic upgrade head || echo "⚠️ Migrations may have already run"

# Check status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "✅ Deployment Complete!"
echo "=================================="
echo "API: http://localhost:2682"
echo "Flower (if enabled): http://localhost:5555"
echo ""
echo "🔒 Security Notes:"
echo "- API bound to localhost:2682 - use Nginx as reverse proxy"
echo "- Database/Redis not exposed externally"
echo "- Add your API keys to .env and restart: docker-compose restart api"
