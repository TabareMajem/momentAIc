"""
SEED EMPIRE
Initialize the 4 Core Startups for the Admin User and Activate Autonomy

Startups:
1. Symbiotask.com
2. Bondquests.com
3. AgentForgeai.com
4. MomentAIc.com
"""

import asyncio
import sys
import os
from uuid import UUID

# FORCE LOCALHOST DB for Script Execution - REMOVED for container execution
# os.environ["DATABASE_URL"] = ...

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.startup import Startup, StartupStage
from app.triggers.default_triggers import create_default_triggers
from app.agents.growth_hacker_agent import growth_hacker_agent
from app.agents.marketing_agent import marketing_agent
from app.services.social_scheduler import social_scheduler
from datetime import datetime, timedelta

# Target User
ADMIN_EMAIL = "tabaremajem@gmail.com"

# The Empire
EMPIRE_STARTUPS = [
    {
        "name": "Symbiotask",
        "url": "https://symbiotask.com",
        "tagline": "The Future of Productivity",
        "description": "AI-powered task management that evolves with you. Symbiotask connects your entire digital life into one symbiotic workflow.",
        "industry": "Productivity"
    },
    {
        "name": "Bondquests",
        "url": "https://bondquests.com",
        "tagline": "Gamified Community Building",
        "description": "Turn community engagement into an epic quest. Bondquests helps communities grow through gamified interactions and rewards.",
        "industry": "Gaming/Community"
    },
    {
        "name": "AgentForge AI",
        "url": "https://agentforgeai.com",
        "tagline": "Build Agents in Seconds",
        "description": "The no-code platform for building, testing, and deploying autonomous AI agents. Forge your digital workforce today.",
        "industry": "AI Infrastructure"
    },
    {
        "name": "MomentAIc",
        "url": "https://momentaic.com",
        "tagline": "Your AI Co-Founder",
        "description": "The Operating System for Entrepreneurs. MomentAIc provides autonomous agents that help you build, grow, and scale your startup.",
        "industry": "SaaS/Startup Tools"
    }
]

async def seed_empire():
    print(f"🚀 INITIALIZING EMPIRE SEED PROTOCOL for {ADMIN_EMAIL}...")
    
    async with AsyncSessionLocal() as db:
        # 1. Get Admin User
        result = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User {ADMIN_EMAIL} not found! Please create this user first.")
            return

        print(f"✅ Found Admin User: {user.full_name} ({user.id})")
        
        # 2. Iterate Startups
        for data in EMPIRE_STARTUPS:
            print(f"\n------------------------------------------------")
            print(f"Processing {data['name']}...")
            
            # Check if exists
            result = await db.execute(select(Startup).where(Startup.website_url == data["url"]))
            startup = result.scalar_one_or_none()
            
            if not startup:
                print(f"🔹 Creating new startup entity...")
                startup = Startup(
                    owner_id=user.id,
                    name=data["name"],
                    tagline=data["tagline"],
                    description=data["description"],
                    industry=data["industry"],
                    stage=StartupStage.MVP,
                    website_url=data["url"],
                    settings={"autopilot_mode": True}, # ENABLING AUTONOMY
                    metrics={}
                )
                db.add(startup)
                await db.flush()
                print(f"✅ Created Startup ID: {startup.id}")
                
                # Default Triggers
                count = await create_default_triggers(db, startup.id, user.id)
                print(f"✅ Created {count} default triggers")
            else:
                print(f"🔹 Startup exists (ID: {startup.id}). Updating settings...")
                # Update autopilot just in case
                if not startup.settings: startup.settings = {}
                startup.settings = {**startup.settings, "autopilot_mode": True}
                db.add(startup)
                await db.flush()
            
            # 3. TRIGGER AUTONOMOUS AGENTS
            print("🤖 Waking up Agents...")
            
            try:
                # Growth Hacker Analysis
                print(f"   ► Growth Hacker Analyzing {data['url']}...")
                
                try:
                    strategy = await growth_hacker_agent.analyze_startup_wizard(
                        url=data["url"],
                        description=data["description"]
                    )
                except Exception as net_err:
                    print(f"     ⚠️ Analysis Network Error: {net_err}. Using FALLBACK Strategy.")
                    strategy = {
                        "viral_post_hook": f"The revolution is here. Meet {data['name']}.",
                        "target_audience": "Innovators and Early Adopters"
                    }
                
                hook = strategy.get("viral_post_hook", f"Discover {data['name']}")
                audience = strategy.get("target_audience", "Early Adopters")
                
                print(f"     Strategy: Target {audience}")
                
                # Marketing Agent - Generate Launch Post
                print("   ► Marketing Agent Creating Launch Post...")
                platforms = ["twitter", "linkedin"]
                
                for platform in platforms:
                    try:
                        post_content = await marketing_agent.create_social_post(
                            context=f"EMPIRE LAUNCH. Product: {data['name']}. Hook: {hook}. Target: {audience}.",
                            platform=platform
                        )
                    except Exception as llm_err:
                         print(f"     ⚠️ LLM Error: {llm_err}. Using FALLBACK Content.")
                         post_content = f"🚀 Launching {data['name']}! {data['tagline']} #startup #launch"

                    # Social Scheduler - Schedule it
                    scheduled_time = datetime.utcnow() + timedelta(minutes=15)
                    await social_scheduler.schedule_post(
                        startup_id=str(startup.id),
                        content=post_content,
                        platforms=[platform],
                        scheduled_at=scheduled_time
                    )
                    print(f"     ✅ Scheduled {platform} post for {scheduled_time.isoformat()}")

            except Exception as e:
                print(f"❌ Agent Error: {e}")
        
        await db.commit()
        print("\n------------------------------------------------")
        print("🚀 EMPIRE SEEDED SUCCESSFULLY.")
        print("All 4 startups active. Autopilot ON. Initial campaigns scheduled.")

if __name__ == "__main__":
    asyncio.run(seed_empire())
