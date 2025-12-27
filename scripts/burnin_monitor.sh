#!/bin/bash
# Staging Burn-in Monitoring Script
# Runs health checks every 15 minutes for 4 hours (16 checks total)
# Start time: 2025-12-26 17:05 UTC+1
# End time:   2025-12-26 21:05 UTC+1

LOG_FILE="/root/momentaic/momentaic-backend/logs/burnin_monitor.log"
HEALTH_URL="http://localhost:9939/api/v1/health"
API_CONTAINER="momentaic-staging-api-staging-1"
WORKER_CONTAINER="momentaic-staging-worker-staging-1"

mkdir -p /root/momentaic/momentaic-backend/logs

echo "========================================" >> "$LOG_FILE"
echo "BURN-IN MONITORING STARTED: $(date)" >> "$LOG_FILE"
echo "Expected end: 4 hours from now" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

check_count=0
max_checks=16  # 4 hours * 4 checks/hour

while [ $check_count -lt $max_checks ]; do
    check_count=$((check_count + 1))
    echo "" >> "$LOG_FILE"
    echo "--- CHECK #$check_count at $(date) ---" >> "$LOG_FILE"
    
    # Health endpoint
    health=$(curl -s "$HEALTH_URL" 2>&1)
    echo "Health: $health" >> "$LOG_FILE"
    
    # Container status
    api_status=$(docker inspect -f '{{.State.Health.Status}}' "$API_CONTAINER" 2>/dev/null || echo "unknown")
    worker_status=$(docker inspect -f '{{.State.Status}}' "$WORKER_CONTAINER" 2>/dev/null || echo "unknown")
    echo "API Status: $api_status" >> "$LOG_FILE"
    echo "Worker Status: $worker_status" >> "$LOG_FILE"
    
    # Resource usage
    echo "Resource Usage:" >> "$LOG_FILE"
    docker stats --no-stream --format "  {{.Name}}: CPU={{.CPUPerc}} MEM={{.MemUsage}}" \
        "$API_CONTAINER" "$WORKER_CONTAINER" 2>/dev/null >> "$LOG_FILE"
    
    # Recent errors in logs
    error_count=$(docker logs --since=15m "$API_CONTAINER" 2>&1 | grep -ci error || echo "0")
    echo "API Errors (last 15m): $error_count" >> "$LOG_FILE"
    
    # Check if healthy
    if echo "$health" | grep -q "healthy"; then
        echo "✅ HEALTHY" >> "$LOG_FILE"
    else
        echo "⚠️  UNHEALTHY OR UNREACHABLE" >> "$LOG_FILE"
    fi
    
    # Wait 15 minutes before next check
    if [ $check_count -lt $max_checks ]; then
        sleep 900  # 15 minutes
    fi
done

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "BURN-IN COMPLETE: $(date)" >> "$LOG_FILE"
echo "Total checks: $check_count" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
