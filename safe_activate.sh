#!/bin/bash
# Safely enable Momentaic without breaking Yorisoi
VPS_IP="72.62.151.245"

echo "Activating Momentaic Config..."

ssh root@$VPS_IP << 'EOF'
    # 1. Force Link Momentaic (Ensure it is enabled)
    ln -sf /etc/nginx/sites-available/momentaic /etc/nginx/sites-enabled/momentaic

    # 2. DO NOT delete Yorisoi (Safe Mode)
    echo "Preserving Yorisoi configuration..."

    # 3. Reload Nginx
    # Warnings about "conflicting server name" are expected but harmless
    # Momentaic (m) loads before Yorisoi (y), so our new config will Win.
    nginx -t && systemctl reload nginx
EOF

echo "✅ Momentaic Enabled (Safe Mode)!"
