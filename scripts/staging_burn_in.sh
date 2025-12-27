#!/bin/bash
# Staging Burn-In Script for High-Assurance Verification
set -e

PROJECT_NAME="momentaic-staging"
BACKEND_DIR="/root/momentaic/momentaic-backend"

echo "🚀 Starting Staging Burn-In Process..."

# 1. Cleanup old staging
docker compose -p $PROJECT_NAME -f $BACKEND_DIR/docker-compose.staging.yml down -v

# 2. Build and start services (Postgres and Redis first)
docker compose -p $PROJECT_NAME -f $BACKEND_DIR/docker-compose.staging.yml up -d --build postgres-staging redis-staging

echo "⏳ Waiting for databases to be healthy..."
sleep 15

# 3. Load Production Schema Dump
echo "📥 Loading production schema dump into staging..."
docker exec momentaic-db-prod pg_dump -U momentaic -s momentaic > /tmp/prod_schema.sql
docker exec -i ${PROJECT_NAME}-postgres-staging-1 psql -U staging_user -d staging_db < /tmp/prod_schema.sql

# 4. Stamp DB to current head (since production is at current head but lacks version table)
echo "📍 Stamping staging DB at head (pre-migration)..."
# We need to run this from a container that has the code and alembic
# We'll use the api-staging service but we must make sure it doesn't crash on init_db
# To prevent crash, we'll run it as a one-off command
docker compose -p $PROJECT_NAME -f $BACKEND_DIR/docker-compose.staging.yml run --rm -e APP_ENV=staging api-staging alembic stamp 002_integrations_triggers

# 5. Apply New Migrations
echo "🆕 Applying new migrations..."
docker compose -p $PROJECT_NAME -f $BACKEND_DIR/docker-compose.staging.yml run --rm -e APP_ENV=staging api-staging alembic upgrade head

# 6. Start full stack
echo "🔥 Starting full stack for 4-hour burn-in..."
docker compose -p $PROJECT_NAME -f $BACKEND_DIR/docker-compose.staging.yml up -d

echo "✅ Staging is LIVE on http://localhost:9939"
echo "📊 Monitor resource usage with: docker stats ${PROJECT_NAME}-api-staging-1"
