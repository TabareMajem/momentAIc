#!/bin/bash
# Force update .env on VPS
ENV_FILE="/root/momentaic/momentaic-backend/env.complete.production"
VPS_IP="72.62.151.245"

echo "Uploading production env file..."
scp "$ENV_FILE" root@$VPS_IP:/opt/momentaic/momentaic-backend/.env

echo "Restarting backend to apply env changes..."
ssh root@$VPS_IP "cd /opt/momentaic/momentaic-backend && docker compose restart api"

echo "✅ Environment Updated!"
