#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"

echo "=== DIAGNOSING VPS CONFIGURATION ==="

sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP << 'EOF'
    echo "--- CHECKING RUNNING PORTS ---"
    netstat -tulpn | grep LISTEN

    echo -e "\n--- CHECKING PM2 LIST ---"
    pm2 list

    echo -e "\n--- CHECKING NGINX SITES ENABLED ---"
    ls -F /etc/nginx/sites-enabled/
    
    echo -e "\n--- CONTENT OF DEFAULT NGINX SITE ---"
    if [ -f /etc/nginx/sites-enabled/default ]; then
        cat /etc/nginx/sites-enabled/default
    fi

    echo -e "\n--- CONTENT OF MOMENTAIC NGINX CONFIG (IF EXISTS) ---"
    grep -r "momentaic" /etc/nginx/sites-enabled/
EOF
