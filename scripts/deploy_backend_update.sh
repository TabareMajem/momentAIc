#!/bin/bash
# Backend Deployment Script (Automated)
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"
REMOTE_DIR="/opt/momentaic/momentaic-backend"

export SSMPASS="$VPS_PASS"

echo "=== BACKEND DEPLOYMENT (AUTOMATED) ==="

# 1. Sync App Code
echo "[1/3] Syncing Backend Code..."
# Sync app folder
sshpass -p "$VPS_PASS" rsync -avz momentaic-backend/app/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/app/"
# Sync alembic migrations
sshpass -p "$VPS_PASS" rsync -avz momentaic-backend/alembic/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/alembic/"
sshpass -p "$VPS_PASS" rsync -avz momentaic-backend/alembic.ini $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
# Sync requirements
sshpass -p "$VPS_PASS" rsync -avz momentaic-backend/requirements.txt $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
# Sync root scripts
sshpass -p "$VPS_PASS" rsync -avz momentaic-backend/*.py $VPS_USER@$VPS_IP:"$REMOTE_DIR/"

# 2. Install & Restart
echo "[2/3] Installing Dependencies & Restarting..."
sshpass -p "$VPS_PASS" ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    cd /opt/momentaic/momentaic-backend
    
    echo "Installing requirements..."
    pip install -r requirements.txt --break-system-packages

    echo "Updating Postgres (Exposing Port)..."
    docker compose up -d postgres
    sleep 5 # Wait for port mapping

    echo "Running Migrations (Inside Docker)..."
    # Run alembic inside the API container (ensure it's running first, or run via run command)
    # We use 'run --rm' to spin up a temporary container for migration if api is not up yet
    # But usually api depends on db.
    
    # Update: best practice is to run migration via docker compose run
    docker compose run --rm api alembic upgrade head
    
    echo "Rebuilding Docker API..."
    docker compose build api celery-worker
    docker compose up -d api celery-worker
    
    # PM2 is legacy/host process, stop it to save resources or restart if still needed
    # pm2 restart momentaic-backend 
    
    echo "=== BACKEND DEPLOYMENT COMPLETE ==="
EOF
