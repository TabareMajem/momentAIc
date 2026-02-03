#!/bin/bash
VPS_IP="72.62.151.245"
VPS_USER="root"
REMOTE_DIR="/opt/momentaic"

echo "=== FINISHING MOMENTAIC DEPLOYMENT ==="

# 1. Sync updated admin script
echo "[1/2] Syncing Admin Script..."
rsync -avz momentaic-backend/create_admin.py $VPS_USER@$VPS_IP:$REMOTE_DIR/momentaic-backend/

# 2. Execute
echo "[2/2] executing Remote Commands..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    
    echo ">>> Creating Admin User..."
    cd /opt/momentaic/momentaic-backend
    # Using PYTHONPATH=/app to ensure imports work
    # File is not mounted, so we must copy it in first
    docker cp create_admin.py momentaic-api-prod:/app/create_admin.py
    docker exec -e PYTHONPATH=/app momentaic-api-prod python create_admin.py "tabaremajem@gmail.com" "88888888" "Tabare Majem"
    
    echo ">>> Building & Restarting Frontend..."
    cd "/opt/momentaic/momentaic front"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    echo "Building Frontend..."
    npm run build
    
    echo "Starting/Restarting PM2 Process..."
    if pm2 list | grep "momentaic-frontend"; then
        pm2 restart momentaic-frontend
    else
        # Start command: serve the dist folder or use vite preview
        # Vite preview default is 4173, forcing port 2685
        pm2 start npm --name "momentaic-frontend" -- run preview -- --port 2685 --host
        pm2 save
    fi
    
    echo "=== DONE! ==="
EOF
