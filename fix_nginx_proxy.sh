#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"

echo "=== FIXING NGINX PROXY TARGET ==="

sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP << 'EOF'
    set -e
    CONF="/etc/nginx/sites-enabled/momentaic.conf"
    
    echo "Current config:"
    grep "proxy_pass" $CONF
    
    # Backup
    cp $CONF "${CONF}.bak"
    
    # Replace port 2685 with 4173 (The PM2/Vite Preview port)
    sed -i 's/127.0.0.1:2685/127.0.0.1:4173/' $CONF
    
    echo "New config:"
    grep "proxy_pass" $CONF
    
    # Test and Restart
    nginx -t
    systemctl reload nginx
    echo "=== NGINX RELOADED ==="
EOF
