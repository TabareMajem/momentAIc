
import asyncio
import sys
import os
from datetime import datetime, timedelta

# ENV VARS will be provided by container
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.startup import Startup
from app.models.social import SocialPost, PostStatus

LAUNCH_CONTENT = {
    "Symbiotask": "Productivity is broken. We fixed it. 🧠✨ \n\nMeet Symbiotask: The first AI that evolves with your workflow. \n\n#AI #Productivity #Launch",
    "Bondquests": "Community is the new moat. 🏰 \n\nTurn your audience into an army with Bondquests. Gamification layer for modern tribes. \n\n#Community #Web3 #Launch",
    "AgentForge AI": "Stop coding agents from scratch. 🤖🔨 \n\nBuild, Deploy, and Scale autonomous workforce in seconds. Welcome to the Forge. \n\n#AI #DevTools #Launch",
    "MomentAIc": "You don't need a co-founder. You need an OS. \n\nMomentAIc is the operating system for the solo-capitalist era. Automate everything. \n\n#Startup #SaaS #Launch"
}

async def force_seed():
    print("🚀 FORCE SEEDING LAUNCH POSTS...")
    async with AsyncSessionLocal() as db:
        # 1. Get Startups
        result = await db.execute(select(Startup))
        startups = result.scalars().all()
        
        count = 0
        for s in startups:
            if s.name in LAUNCH_CONTENT:
                content = LAUNCH_CONTENT[s.name]
                
                # Check if post already exists to avoid dupes
                # (Simple check)
                
                post = SocialPost(
                    startup_id=s.id,
                    content=content,
                    platforms=["twitter", "linkedin"],
                    scheduled_at=datetime.utcnow() + timedelta(minutes=15),
                    status=PostStatus.SCHEDULED
                )
                db.add(post)
                count += 1
                print(f"   [+] Scheduled post for {s.name}")
        
        await db.commit()
        print(f"✅ Successfully queued {count} launch posts.")

if __name__ == "__main__":
    asyncio.run(force_seed())
