#!/bin/bash
VPS_IP="72.62.151.245"
VPS_USER="root"
REMOTE_DIR="/opt/momentaic/momentaic-backend"

echo "=== DEPLOYING BACKEND (CODE + ENV) ==="

# 1. Sync env file
echo "[1/3] Syncing environment variables..."
rsync -avz "momentaic-backend/env.complete.production" $VPS_USER@$VPS_IP:$REMOTE_DIR/.env

# 2. Sync Application Code (Vital for new Features/Agents)
echo "[2/3] Syncing Application Code..."
rsync -avz --exclude '__pycache__' "momentaic-backend/app" $VPS_USER@$VPS_IP:$REMOTE_DIR/

# 3. Recreate Container
echo "[3/3] Recreating Backend Container..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    cd /opt/momentaic/momentaic-backend
    
    # Force recreate api service to pick up new code & env
    echo "Running docker compose up -d --build --force-recreate api..."
    # --build ensures we repackage the python files if COPY is used (though volumes might handle it, build is safer)
    docker compose up -d --build --force-recreate api || docker-compose up -d --build --force-recreate api
    
    echo "=== DEPLOYMENT COMPLETE ==="
EOF
