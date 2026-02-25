import asyncio
import os
import asyncpg
from dotenv import load_dotenv

# Load env from .env file directly to verify file content
load_dotenv("/root/momentaic/momentaic-backend/.env")

DB_URL = os.getenv("DATABASE_URL")
print(f"Loaded DATABASE_URL from file: {DB_URL}")

async def test_connect():
    print(f"Attempting to connect to: {DB_URL}")
    try:
        conn = await asyncpg.connect(DB_URL)
        print("✅ Connection successful!")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    # Fallback Test: Try strict 127.0.0.1
    print("\nAttempting strict 127.0.0.1 connection...")
    try:
        # construct manual url
        # postgresql+asyncpg://momentaic:17122f617a04c22b1821e4344aab9f8a@127.0.0.1:5432/momentaic
        # asyncpg url format: postgres://user:password@host:port/database
        # NOTE: sqlalchemy uses postgresql+asyncpg, asyncpg uses postgresql://
        
        base_url = DB_URL.replace("postgresql+asyncpg://", "postgresql://").replace("localhost", "127.0.0.1")
        print(f"Testing URL: {base_url}")
        conn = await asyncpg.connect(base_url)
        print("✅ 127.0.0.1 Connection successful!")
        await conn.close()
    except Exception as e:
        print(f"❌ 127.0.0.1 Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
