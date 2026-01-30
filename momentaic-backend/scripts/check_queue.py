
import asyncio
import sys
import os
from datetime import datetime

# Configure DB connection for script
# Uses environment variables from container
# os.environ["DATABASE_URL"] = ...
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.social import SocialPost

from app.models.startup import Startup

async def check_queue():
    print("🔎 Checking DB State...")
    async with AsyncSessionLocal() as db:
        # Check Startups
        result = await db.execute(select(Startup))
        startups = result.scalars().all()
        print(f"✅ Found {len(startups)} Startups in DB.")
        for s in startups:
            print(f"   - {s.name} ({s.id})")

        # Check Posts
        result = await db.execute(select(SocialPost))
        posts = result.scalars().all()
        
        print(f"✅ Found {len(posts)} total posts in database.")
        for p in posts:
            print(f"   - ID: {p.id}")
            print(f"     Status: {p.status}")
            print(f"     Scheduled: {p.scheduled_at}")
            print(f"     Content: {p.content}")
            print(f"     Platforms: {p.platforms}")
            print("---")

if __name__ == "__main__":
    asyncio.run(check_queue())
