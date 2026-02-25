#!/bin/bash
VPS_IP="207.180.227.179"
VPS_USER="root"
LOG_FILE="backend_crash_logs.txt"

echo "=== CAPTURING BACKEND LOGS ===" | tee $LOG_FILE

echo "" >> $LOG_FILE
echo "=== Container Status ===" >> $LOG_FILE
ssh $VPS_USER@$VPS_IP "docker ps -a | grep momentaic" >> $LOG_FILE 2>&1

echo "" >> $LOG_FILE
echo "=== Last 100 Lines of API Logs ===" >> $LOG_FILE
ssh $VPS_USER@$VPS_IP "docker logs momentaic-api-prod --tail 100" >> $LOG_FILE 2>&1

echo "" >> $LOG_FILE
echo "=== Health Check Test ===" >> $LOG_FILE
ssh $VPS_USER@$VPS_IP "curl -s http://127.0.0.1:8839/api/v1/health || echo 'Health check failed'" >> $LOG_FILE 2>&1

echo "" >> $LOG_FILE
echo "=== Current .env PORT setting ===" >> $LOG_FILE
ssh $VPS_USER@$VPS_IP "grep PORT /opt/momentaic/momentaic-backend/.env" >> $LOG_FILE 2>&1

echo ""
echo "Logs saved to: $LOG_FILE"
echo "=== DONE ==="
cat $LOG_FILE
