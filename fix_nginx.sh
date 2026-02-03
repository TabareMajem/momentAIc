#!/bin/bash
# Fix Nginx Proxy Config
# Maps momentaic.com -> Frontend (2685) and /api -> Backend (8839)

VPS_IP="72.62.151.245"
NGINX_CONF="/etc/nginx/sites-available/momentaic"

echo "Creating correct Nginx configuration..."
cat > nginx.conf << 'EOF'
server {
    server_name momentaic.com www.momentaic.com;

    # Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:2685;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API (FastAPI)
    location /api {
        proxy_pass http://127.0.0.1:8839;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/momentaic.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/momentaic.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = www.momentaic.com) {
        return 301 https://$host$request_uri;
    }
    if ($host = momentaic.com) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name momentaic.com www.momentaic.com;
    return 404; # managed by Certbot
}
EOF

echo "Uploading Nginx config..."
scp nginx.conf root@$VPS_IP:$NGINX_CONF

echo "Reloading Nginx..."
ssh root@$VPS_IP "nginx -t && systemctl reload nginx"

echo "✅ Nginx Fixed!"
