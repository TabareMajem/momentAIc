#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"

echo "=== CLEANING UP NGINX & RELOADING ==="

sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP << 'EOF'
    # Remove the backup file from enabled sites (it causes conflict)
    rm /etc/nginx/sites-enabled/momentaic.conf.bak
    
    # Reload Nginx
    nginx -t
    systemctl reload nginx
    echo "=== NGINX RELOADED CLEANLY ==="
    
    # Restart PM2 Frontend to be sure
    pm2 restart momentaic-frontend
EOF
