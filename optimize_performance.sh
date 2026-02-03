#!/bin/bash

# Configuration
VPS_USER="root"
VPS_HOST="72.62.151.245"
VPS_DIR="/var/www/momentaic/momentaic-backend"
LOCAL_DIR="/root/momentaic/momentaic-backend"

echo "🚀 Starting Performance Optimization Deployment..."

# 1. Upload modified configuration files
echo "📤 Uploading optimized config files..."
scp $LOCAL_DIR/app/core/config.py $VPS_USER@$VPS_HOST:$VPS_DIR/app/core/config.py
scp $LOCAL_DIR/docker-compose.yml $VPS_USER@$VPS_HOST:$VPS_DIR/docker-compose.yml

# 2. Restart Backend to apply changes
echo "🔄 Restarting Backend Service to apply new limits..."
ssh $VPS_USER@$VPS_HOST << EOF
    cd $VPS_DIR
    
    # Recreate container to apply docker-compose resource limits
    docker-compose down api
    docker-compose up -d --no-deps --build api
    
    echo "✅ Optimization applied. Verifying limits..."
    docker stats momentaic-api-prod --no-stream
EOF

echo "✨ Performance optimization complete!"
