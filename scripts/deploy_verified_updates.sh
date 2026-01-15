#!/bin/bash
# SAFE DEPLOYMENT SCRIPT
# Use this to deploy the currently verified code from /root/momentaic to /opt/momentaic

set -e

SOURCE_DIR="/root/momentaic/momentaic-backend"
DEST_DIR="/opt/momentaic/momentaic-backend"
BACKUP_DIR="/opt/momentaic/backups/$(date +%Y%m%d_%H%M%S)"

echo "=== MOMENTAIC SAFE DEPLOYMENT ==="
echo ""

# 1. Validation (Double Check)
echo "[1/4] Re-verifying code safety..."
bash /root/momentaic/scripts/validate_before_deploy.sh

# 2. Backup
echo ""
echo "[2/4] Creating backup of current production..."
mkdir -p "$BACKUP_DIR"
if [ -d "$DEST_DIR" ]; then
    cp -r "$DEST_DIR" "$BACKUP_DIR"
    echo "✅ Backup saved to $BACKUP_DIR"
else
    echo "⚠️ Destination $DEST_DIR not found. Skipping backup (nothing to back up)."
fi

# 3. Sync Files
echo ""
echo "[3/4] Syncing verified code to production..."
mkdir -p "$DEST_DIR"
# Sync app directory (code), avoiding .env or git files
# Trailing slash on SOURCE_DIR/ means "copy contents of this dir"
# No trailing slash on DEST_DIR means "copy into this dir" (if it existed as folder in rsync logic, but here we want contents)
# Correct rsync to copy CONTENTS of backend to DEST_DIR
rsync -av \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='venv' \
    "$SOURCE_DIR/" "$DEST_DIR/"

echo "✅ Code synced (including docker-compose.yml)."

# 4. Restart
echo ""
echo "[4/4] Restarting Services..."
cd /opt/momentaic/momentaic-backend
if command -v pm2 &> /dev/null; then
    pm2 restart momentaic-backend
    echo "✅ PM2 Restarted."
else
    echo "⚠️ PM2 not found in path. Rebuilding and restarting all Docker containers..."
    docker compose up -d --build
    
    echo ""
    echo "[5/5] Running database migrations..."
    # Wait a bit for api to be ready enough for exec
    sleep 10
    docker compose exec -T api alembic upgrade head
fi

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "Check logs: pm2 logs momentaic-backend --lines 50"
