#!/bin/bash
set -e

echo "====================================="
echo "  Momentaic Deployment Verification  "
echo "====================================="

echo "[1/5] Checking Docker Container Statuses..."
CRASHED=$(docker ps -a --format '{{.Names}} {{.State}}' | grep momentaic | grep -v 'running' || true)
if [ -n "$CRASHED" ]; then
    echo "❌ ERROR: Found non-running containers:"
    echo "$CRASHED"
    exit 1
else
    echo "✅ All containers are in 'running' state."
fi

echo "[2/5] Checking for Hidden Process Crash Loops / Connection Refusals in Logs..."
LOG_ERRORS=$(docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --since 1m | grep -iE "ConnectionRefusedError|Traceback|Application startup failed|object.__init__|TypeError|Temporary failure in name resolution" || true)

if [ -n "$LOG_ERRORS" ]; then
    echo "❌ ERROR: Found critical exceptions in the logs indicating a crash loop:"
    echo "$LOG_ERRORS" | head -n 20
    exit 1
else
    echo "✅ No critical exceptions found in recent logs."
fi

echo "[3/5] Checking API Health Endpoint..."
MAX_RETRIES=10
RETRY_COUNT=0
HTTP_STATUS=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8839/api/v1/health || true)
    if [ "$HTTP_STATUS" == "200" ]; then
        echo "✅ API Healthcheck passed (HTTP 200)."
        break
    fi
    echo "  ...API not ready yet (status: $HTTP_STATUS), waiting 5s... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ ERROR: API Healthcheck failed to return 200 after 50 seconds."
    exit 1
fi

echo "[4/5] Checking Celery Worker Ping..."
CELERY_PING=$(docker exec momentaic-worker-prod celery -A app.tasks.celery_app inspect ping || true)
if [[ $CELERY_PING == *"pong"* || $CELERY_PING == *"OK"* ]]; then
    echo "✅ Celery Worker is responsive to pings."
else
    echo "❌ ERROR: Celery Worker did not respond correctly to ping."
    echo "Output: $CELERY_PING"
    exit 1
fi

echo "[5/5] Final Uptime Verification..."
docker ps --format "table {{.Names}}\t{{.Status}}" | grep momentaic

echo "====================================="
echo "✅ DEPLOYMENT FULLY VERIFIED SUCCESS ✅"
echo "====================================="
