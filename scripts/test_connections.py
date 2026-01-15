import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from redis import Redis

async def test_all():
    env_file = "/opt/momentaic/momentaic-backend/.env"
    print(f"Reading {env_file}...")
    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip('"')

    db_url = os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL")
    
    print(f"Testing DB: {db_url}")
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✅ Database: CONNECTED")
    except Exception as e:
        print(f"❌ Database: FAILED - {e}")

    print(f"Testing Redis: {redis_url}")
    try:
        r = Redis.from_url(redis_url)
        r.ping()
        print("✅ Redis: CONNECTED")
    except Exception as e:
        print(f"❌ Redis: FAILED - {e}")

if __name__ == "__main__":
    asyncio.run(test_all())
