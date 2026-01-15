
import asyncio
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import engine
from sqlalchemy import text

async def cleanup():
    print("Cleaning up partial migration state...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS action_items CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS actionpriority CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS actionstatus CASCADE"))
    print("Cleanup done.")

if __name__ == "__main__":
    asyncio.run(cleanup())
