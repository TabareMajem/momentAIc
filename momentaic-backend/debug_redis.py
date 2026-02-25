import asyncio
import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv("/root/momentaic/momentaic-backend/.env")

REDIS_URL = os.getenv("REDIS_URL")
print(f"Testing REDIS_URL: {REDIS_URL}")

async def test_redis():
    try:
        r = redis.from_url(REDIS_URL)
        await r.ping()
        print("✅ Redis Connection successful!")
        await r.close()
    except Exception as e:
        print(f"❌ Redis Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis())
