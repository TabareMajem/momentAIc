# MomentAIc Database Initialization
# Run this on first deployment to set up PostgreSQL with required extensions

This directory should contain:
- Database setup instructions (this file)
- Migration commands

## Required PostgreSQL Extensions

Add to your init script or run manually:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
SET timezone = 'UTC';
```

## Running Migrations

```bash
# From the momentaic-backend directory
docker-compose exec api alembic upgrade head

# Or if running locally:
alembic upgrade head
```

## Note

The `.gitignore` excludes `.sql` files for security.
For production, create the init-db.sql manually on the server:

```bash
cat > scripts/init-db.sql << 'EOF'
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
SET timezone = 'UTC';
EOF
```
