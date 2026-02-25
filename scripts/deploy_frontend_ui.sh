#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"
REMOTE_DIR="/opt/momentaic"

echo "=== DEPLOYING FRONTEND UI UPDATES ==="

# 1. Sync updated files
echo "[1/2] Syncing Frontend Code & Build..."
export SSMPASS="$VPS_PASS"

# Sync dependencies config
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/package.json" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/"

# Sync Source (for reference/backup)
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/pages/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/pages/"
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/App.tsx" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/"
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/components/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/components/"
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/lib/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/lib/"
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/src/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/src/"

# Sync Build (The important part)
sshpass -p "$VPS_PASS" rsync -avz "momentaic-frontend/dist/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic-frontend/dist/"

# 2. Rebuild & Restart
echo "[2/2] Restarting Frontend..."
sshpass -p "$VPS_PASS" ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    cd "/opt/momentaic/momentaic-frontend"
    
    # Install new deps (react-markdown)
    echo "Installing new deps..."
    npm install
    
    # Restart
    pm2 restart momentaic-frontend
    
    echo "=== UI UPDATE COMPLETE ==="
EOF
