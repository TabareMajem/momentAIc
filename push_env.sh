#!/bin/bash
# Force update .env on VPS
ENV_FILE="/root/momentaic/momentaic-backend/env.complete.production"
VPS_IP="207.180.227.179"

echo "Uploading production env file..."
sshpass -p "Yokaizen14-88888888" scp -o StrictHostKeyChecking=no "$ENV_FILE" root@$VPS_IP:/opt/momentaic/momentaic-backend/.env
sshpass -p "Yokaizen14-88888888" scp -o StrictHostKeyChecking=no "/root/momentaic/momentaic-backend/app/core/service_account.json" root@$VPS_IP:/opt/momentaic/momentaic-backend/app/core/service_account.json

echo "Restarting backend to apply env changes..."
sshpass -p "Yokaizen14-88888888" ssh -o StrictHostKeyChecking=no root@$VPS_IP "cd /opt/momentaic/momentaic-backend && docker compose restart api"

echo "✅ Environment Updated!"
