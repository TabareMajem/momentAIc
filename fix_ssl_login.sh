#!/bin/bash
VPS_IP="72.62.151.245"
VPS_USER="root"
REMOTE_DIR="/opt/momentaic"

echo "=== FIXING SSL LOGIN ISSUES ==="

# 1. Sync updated files
echo "[1/4] Syncing Configs..."
rsync -avz momentaic-backend/nginx/momentaic.conf $VPS_USER@$VPS_IP:$REMOTE_DIR/momentaic-backend/nginx/
rsync -avz "momentaic front/.env.production" $VPS_USER@$VPS_IP:$REMOTE_DIR/"momentaic front/"

# 2. Execute Fixes
echo "[2/4] Applying Nginx Fix & Rebuilding Frontend..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    
    # 1. Update Nginx Config
    echo ">>> Updating Nginx..."
    cp /opt/momentaic/momentaic-backend/nginx/momentaic.conf /etc/nginx/sites-available/momentaic.conf
    # Ensure link exists
    ln -sf /etc/nginx/sites-available/momentaic.conf /etc/nginx/sites-enabled/momentaic.conf
    
    # Reload Nginx
    if nginx -t; then
        systemctl reload nginx
        echo "✅ Nginx Reloaded"
    else
        echo "❌ Nginx Config Invalid!"
        exit 1
    fi
    
    # 2. Rebuild Frontend
    echo ">>> Rebuilding Frontend (Switching to relative API path)..."
    cd "/opt/momentaic/momentaic front"
    
    # Ensure env is loaded or just present
    # .env.production is already there from rsync
    
    npm run build
    
    # 3. Restart PM2
    echo ">>> Restarting Frontend Process..."
    pm2 restart momentaic-frontend
    
    echo "=== DONE! Login should work now at https://momentaic.com/login ==="
EOF
