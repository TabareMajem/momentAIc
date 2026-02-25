#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"

echo "=== FINDING NGINX CONFLICTS ==="

sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP << 'EOF'
    grep -r "momentaic.com" /etc/nginx/sites-enabled/
EOF
