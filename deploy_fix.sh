#!/bin/bash

# MOMENTAIC MASTER DEPLOYMENT FIX SCRIPT
# Run this from your LOCAL terminal (where momentaic folder is)

VPS_IP="62.72.56.216"
VPS_USER="root"
REMOTE_DIR="/opt/momentaic"

echo "==============================================="
echo "   MOMENTAIC DEPLOYMENT FIXER"
echo "==============================================="

# 1. Sync Backend Code (Fixes 500 & Port)
echo "[1/4] Syncing Backend..."
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' --exclude='.env' \
  momentaic-backend/ $VPS_USER@$VPS_IP:$REMOTE_DIR/momentaic-backend/

# 2. Sync Frontend Code (Fixes Hero Message)
echo "[2/4] Syncing Frontend (Landing Page fix)..."
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='dist' \
  "momentaic front/" $VPS_USER@$VPS_IP:$REMOTE_DIR/"momentaic front/"

# 3. Execute Remote Commands
echo "[3/4] Connecting to VPS to Rebuild & Fix..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e

    echo ">>> VPS: Fixing Backend..."
    cd /opt/momentaic/momentaic-backend
    
    # Ensure correct .env
    cp env.complete.production .env
    
    # Rebuild Backend containers (Force 8839)
    # Removing orphans to clean up any old port mappings
    docker compose down --remove-orphans
    docker compose up -d --build
    
    # Wait for API to be ready
    echo ">>> Waiting for API startup (15s)..."
    sleep 15
    
    # Verify API Health
    if curl -s http://localhost:8839/api/v1/health | grep "healthy"; then
        echo "✅ API is HEALTHY on port 8839!"
    else
        echo "❌ API check failed on 8839. Checking logs..."
        docker logs momentaic-api-prod --tail 20
    fi
    
    # Run Admin Creation Script
    echo ">>> Creating Admin User..."
    docker exec -e PYTHONPATH=/app momentaic-api-prod python create_admin.py "tabaremajem@gmail.com" "88888888" "Tabare Majem"
    
    echo ">>> VPS: Fixing Frontend..."
    cd "/opt/momentaic/momentaic front"
    
    # Check if frontend process is needed
    # Assuming frontend is served via 'npm run preview' on 2685 managed by PM2 or similar
    # If not running, we build and start it
    
    if ! netstat -tulpn | grep 2685; then
        echo "⚠️  Frontend port 2685 NOT LISTENING. Attempting build & start..."
        
        # Install dependencies if needed (skip if node_modules exists to save time)
        if [ ! -d "node_modules" ]; then
            npm install
        fi
        
        # Build 
        npm run build
        
        # Start with PM2
        if pm2 list | grep "momentaic-frontend"; then
            pm2 restart momentaic-frontend
        else
            pm2 start npm --name "momentaic-frontend" -- run preview -- --port 2685 --host
        fi
        pm2 save
    else
        echo "✅ Frontend is LISTENING on 2685. Reloading..."
        # If running via PM2, reload to pick up LandingPage changes
        pm2 restart momentaic-frontend || echo "Could not restart PM2 process, functionality might be stale."
        # If running via Docker, restart it
    fi

EOF

echo "==============================================="
echo "   DEPLOYMENT COMPLETE!"
echo "==============================================="
