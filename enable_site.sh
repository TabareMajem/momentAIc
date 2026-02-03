#!/bin/bash
# Enable Momentaic and disable conflicts
VPS_IP="72.62.151.245"

echo "Running Nginx fix on VPS..."

ssh root@$VPS_IP << 'EOF'
    # 1. Enable the correct site
    ln -sf /etc/nginx/sites-available/momentaic /etc/nginx/sites-enabled/momentaic

    # 2. Disable the CONFIRMED conflicting site (yorisoiai.conf)
    # The previous logs showed it was hijacking 'momentaic.com' on line 40
    if [ -f /etc/nginx/sites-enabled/yorisoiai.conf ]; then
        echo "Disabling conflicting config: yorisoiai.conf"
        mv /etc/nginx/sites-enabled/yorisoiai.conf /etc/nginx/sites-available/yorisoiai.conf.disabled
        rm -f /etc/nginx/sites-enabled/yorisoiai.conf
    fi

    # 3. Reload
    nginx -t && systemctl reload nginx
EOF

echo "✅ Site Enabled & Conflicts Removed!"
