#!/bin/bash
VPS_IP="62.72.56.216"
VPS_USER="root"
REMOTE_DIR="/opt/momentaic"

echo "=== DEPLOYING FRONTEND UI UPDATES ==="

# 1. Sync updated files
echo "[1/2] Syncing Frontend Code..."

# Sync entire entries to catch new pages (like CoFounderMatch.tsx)
rsync -avz "momentaic front/pages/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic front/pages/"
rsync -avz "momentaic front/App.tsx" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic front/"
rsync -avz "momentaic front/components/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic front/components/"
rsync -avz "momentaic front/lib/" $VPS_USER@$VPS_IP:"$REMOTE_DIR/momentaic front/lib/"

# 2. Rebuild & Restart
echo "[2/2] Rebuilding Frontend..."
ssh $VPS_USER@$VPS_IP << 'EOF'
    set -e
    cd "/opt/momentaic/momentaic front"
    
    # Rebuild
    npm run build
    
    # Restart
    pm2 restart momentaic-frontend
    
    echo "=== UI UPDATE COMPLETE ==="
EOF
