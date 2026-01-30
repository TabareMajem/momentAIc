
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.growth import Lead
from app.models.startup import Sprint

async def verify_strategic_targets():
    print("🎯 VERIFYING STRATEGIC TARGETS...")
    async with AsyncSessionLocal() as db:
        # Check for Bilawal (Symbiotask Target)
        bilawal = await db.execute(select(Lead).where(Lead.contact_name == "Bilawal Sidhu"))
        if bilawal.scalar_one_or_none():
            print("✅ FOUND: Bilawal Sidhu (Technical Creative)")
        else:
            print("❌ MISSING: Bilawal Sidhu")

        # Check for Ole (Ambassador Target)
        ole = await db.execute(select(Lead).where(Lead.contact_name == "Ole Lehmann"))
        if ole.scalar_one_or_none():
            print("✅ FOUND: Ole Lehmann (Ambassador)")
        else:
            print("❌ MISSING: Ole Lehmann")

        # Check total Sprints
        sprints = await db.execute(select(Sprint))
        sprint_list = sprints.scalars().all()
        print(f"🏃 Active Sprints: {len(sprint_list)}")
        for s in sprint_list:
            if "Product Hunt" in s.goal:
                print(f"   - Sprint: {s.goal}")

if __name__ == "__main__":
    asyncio.run(verify_strategic_targets())
