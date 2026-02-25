#!/bin/bash
# Update dependencies and rebuild
# The VPS has an old requirements.txt, so the new AI libraries aren't installed!

VPS_IP="207.180.227.179"

echo "1. Uploading updated requirements.txt..."
scp /root/momentaic/momentaic-backend/requirements.txt root@$VPS_IP:/opt/momentaic/momentaic-backend/

echo "2. Rebuilding backend container (installing new libs)..."
ssh root@$VPS_IP "cd /opt/momentaic/momentaic-backend && docker compose up -d --build --force-recreate api"

echo "✅ Dependencies Updated & Backend Rebuilt"
