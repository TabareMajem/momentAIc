
import asyncio
import sys
import os

# ENV VARS will be provided by container
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.growth import Lead
from app.models.startup import Sprint

async def check_growth_status():
    print("🕵️ GROWTH STATUS AUDIT...")
    async with AsyncSessionLocal() as db:
        # Check Leads
        result = await db.execute(select(Lead))
        leads = result.scalars().all()
        print(f"📉 Total Leads: {len(leads)}")
        
        # Check Sprints
        result = await db.execute(select(Sprint))
        sprints = result.scalars().all()
        print(f"🏃 Total Sprints: {len(sprints)}")

        if len(leads) == 0:
            print("❌ CONCLUSION: No growth targets seeded. Agents are idle.")
        else:
            print("✅ CONCLUSION: Growth engine is active.")

if __name__ == "__main__":
    asyncio.run(check_growth_status())
