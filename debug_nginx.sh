#!/bin/bash
VPS_IP="72.62.151.245"
VPS_USER="root"
LOG_FILE="nginx_error_log.txt"

echo "=== CAPTURING NGINX LOGS ==="

echo "=== Last 50 lines of Nginx Error Log ===" > $LOG_FILE
ssh $VPS_USER@$VPS_IP "tail -n 50 /var/log/nginx/error.log" >> $LOG_FILE 2>&1

echo "" >> $LOG_FILE
echo "=== Nginx Config Check ===" >> $LOG_FILE
ssh $VPS_USER@$VPS_IP "nginx -t" >> $LOG_FILE 2>&1

echo "Logs saved to: $LOG_FILE"
cat $LOG_FILE
