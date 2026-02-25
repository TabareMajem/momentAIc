#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
VPS_PASS="Yokaizen14-88888888"

echo "=== READING MOMENTAIC NGINX CONF ==="

sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "cat /etc/nginx/sites-enabled/momentaic.conf"
