import asyncio
import sys
import os
import glob
from sqlalchemy import select

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import async_session_maker
from app.models.growth import Lead, LeadStatus, LeadSource
from app.models.startup import Startup

async def seed_leads():
    async with async_session_maker() as db:
        # Get a default startup (Yokaizen)
        result = await db.execute(select(Startup))
        startup = result.scalar_one_or_none()
        
        if not startup:
            print("No startup found. Please run init-db first.")
            return

        print(f"Seeding leads for startup: {startup.name}")
        
        # Parse log files
        log_files = ["/app/campaign_log.md"]
        leads_added = 0
        
        for log_file in log_files:
            print(f"Reading {log_file}...")
            with open(log_file, "r") as f:
                content = f.read()
                
            # Naive parsing of "## 🎯 Prospect: Company Name"
            lines = content.split('\n')
            for line in lines:
                if line.startswith("## 🎯 Prospect:"):
                    company_name = line.replace("## 🎯 Prospect:", "").strip()
                    
                    # Check if exists
                    exists = await db.execute(
                        select(Lead).where(
                            Lead.company_name == company_name,
                            Lead.startup_id == startup.id
                        )
                    )
                    if exists.scalar_one_or_none():
                        continue
                        
                    # Create Lead
                    lead = Lead(
                        startup_id=startup.id,
                        company_name=company_name,
                        contact_name="Admissions Manager", # Placeholder
                        source=LeadSource.COLD_OUTREACH,
                        status=LeadStatus.NEW,
                        notes="Imported from scaled campaign log"
                    )
                    db.add(lead)
                    leads_added += 1
        
        await db.commit()
        print(f"✅ Successfully seeded {leads_added} leads into the database.")

if __name__ == "__main__":
    asyncio.run(seed_leads())
