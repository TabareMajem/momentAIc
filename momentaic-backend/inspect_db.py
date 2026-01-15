
import asyncio
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import engine
from sqlalchemy import text

async def inspect():
    print("Inspecting DB state...")
    async with engine.connect() as conn:
        # Check tables
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables: {tables}")
        
        # Check types
        result = await conn.execute(text("SELECT typname FROM pg_type WHERE typnamespace = 'public'::regnamespace"))
        types = [row[0] for row in result.fetchall()]
        print(f"Types: {types}")

if __name__ == "__main__":
    asyncio.run(inspect())
