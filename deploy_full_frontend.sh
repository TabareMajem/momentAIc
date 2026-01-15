#!/bin/bash
# Full Frontend Deployment - Includes Assets, Pages, Components
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"
REMOTE_DIR="/opt/momentaic/momentaic-frontend"

export SSMPASS="$VPS_PASS"

echo "=== FULL FRONTEND DEPLOYMENT (AUTOMATED) ==="

# 1. Build locally first
echo "[1/4] Building Frontend..."
cd /root/momentaic/momentaic-frontend
npm run build

# 2. Sync entire dist folder (includes assets)
echo "[2/4] Syncing Built Files..."
sshpass -p "$VPS_PASS" rsync -avz --progress dist/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/dist/"

# 3. Sync source files for server-side rebuild if needed
echo "[3/4] Syncing Source Files..."
sshpass -p "$VPS_PASS" rsync -avz pages/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/pages/"
sshpass -p "$VPS_PASS" rsync -avz components/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/components/"
sshpass -p "$VPS_PASS" rsync -avz lib/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/lib/"
sshpass -p "$VPS_PASS" rsync -avz stores/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/stores/"
sshpass -p "$VPS_PASS" rsync -avz App.tsx $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
sshpass -p "$VPS_PASS" rsync -avz index.html $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
sshpass -p "$VPS_PASS" rsync -avz public/ $VPS_USER@$VPS_IP:"$REMOTE_DIR/public/"

# Sync Config Files (Essential for build)
sshpass -p "$VPS_PASS" rsync -avz package.json $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
sshpass -p "$VPS_PASS" rsync -avz postcss.config.js $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
sshpass -p "$VPS_PASS" rsync -avz tailwind.config.js $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
sshpass -p "$VPS_PASS" rsync -avz vite.config.ts $VPS_USER@$VPS_IP:"$REMOTE_DIR/"
sshpass -p "$VPS_PASS" rsync -avz tsconfig.json $VPS_USER@$VPS_IP:"$REMOTE_DIR/" # If exists
sshpass -p "$VPS_PASS" rsync -avz tsconfig.app.json $VPS_USER@$VPS_IP:"$REMOTE_DIR/" # If exists
sshpass -p "$VPS_PASS" rsync -avz tsconfig.node.json $VPS_USER@$VPS_IP:"$REMOTE_DIR/" # If exists

# 4. Restart on VPS
echo "[4/4] Installing Dependencies & Restarting..."
sshpass -p "$VPS_PASS" ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    cd /opt/momentaic/momentaic-frontend
    
    # Install dependencies (including new ones like framer-motion)
    npm install
    
    # Rebuild
    npm run build
    
    # Restart
    pm2 restart momentaic-frontend || pm2 start npm --name "momentaic-frontend" -- run preview
    echo "=== DEPLOYMENT COMPLETE ==="
EOF

echo "✅ Full deployment finished!"
