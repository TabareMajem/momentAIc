
import asyncio
import structlog
from app.core.database import AsyncSessionLocal
from app.models.startup import Startup
from app.models.user import User, UserTier
from app.agents.marketing_agent import marketing_agent
from app.agents.sales_agent import sales_agent
from sqlalchemy import select
from uuid import uuid4

logger = structlog.get_logger()

INTERNAL_PRODUCTS = [
    {
        "name": "AgentForge AI",
        "description": "The ultimate No-Code AI Agent Builder. Build, deploy, and monetize autonomous agents on the blockchain. Create swarms without coding using a visual interface.",
        "industry": "AI & Blockchain DevTools",
        "url": "https://agentforgeai.com",
        "target_audience": "Developers, Crypto Founders, AI Enthusiasts"
    },
    {
        "name": "BondQuests",
        "description": "Gamified habit tracker and adventure RPG for couples. Strengthern your relationship by completing real-world quests together. Level up your love life.",
        "industry": "Consumer App / Health & Wellness",
        "url": "https://bondquests.com",
        "target_audience": "Couples, Gamers, Gen Z"
    },
    {
        "name": "SymbioTask",
        "description": "AI-powered Project Management that adapts to your team's biology and workflow. Symbiotic productivity that learns how you work best.",
        "industry": "B2B SaaS / Productivity",
        "url": "https://symbiotask.com",
        "target_audience": "Remote Teams, Agile Startups"
    }
]

async def dogfood_launch():
    print("🚀 DOGFOOD LAUNCH PROTOCOL INITIATED")
    
    async with AsyncSessionLocal() as db:
        # 0. Get Owner (Target User)
        target_email = "tabaremajem@gmail.com"
        result = await db.execute(select(User).where(User.email == target_email))
        owner = result.scalars().first()
        
        if not owner:
            print(f"Creating User: {target_email}...")
            owner = User(
                id=uuid4(),
                email=target_email,
                hashed_password="hashed_placeholder_admin", 
                full_name="Tabare Majem",
                tier=UserTier.GOD_MODE,
                credits_balance=999999,
                is_superuser=True,
                is_verified=True
            )
            db.add(owner)
            await db.commit()
            await db.refresh(owner)
        
        print(f"✅ Target User: {owner.email} ({owner.id})")

        for product in INTERNAL_PRODUCTS:
            print(f"\n✨ Processing {product['name']}...")
            
            # 1. Get or Create Startup (Case Insensitive)
            result = await db.execute(select(Startup).where(Startup.name.ilike(product['name'])))
            startup = result.scalars().first()
            
            if not startup:
                print(f"Creating new startup record for {product['name']}...")
                startup = Startup(
                    id=uuid4(),
                    owner_id=owner.id,
                    name=product['name'],
                    description=product['description'],
                    industry=product['industry'],
                    website_url=product['url'],
                    stage="Launch"
                )
                db.add(startup)
                await db.commit()
                await db.refresh(startup)
            else:
                 print(f"Found existing record: {startup.id}. Updating Owner...")
                 startup.owner_id = owner.id
                 db.add(startup)
                 await db.commit()
                 print(f"✅ Ownership transferred to {target_email}")

            startup_context = {
                "name": startup.name,
                "description": startup.description,
                "industry": startup.industry,
                "url": startup.website_url
            }

            # 2. Trigger Marketing Agent (Strategy)
            print("   🤖 Marketing Agent: Generating Campaign Plan...")
            try:
                plan = await marketing_agent.generate_campaign_plan(
                    template_name="Viral Launch",
                    startup_context=startup_context
                )
                print(f"      ✅ Plan Generated: {plan.get('name')} ({len(plan.get('tasks', []))} tasks)")
                
                # Check for Social Launch Post
                print("   🤖 Marketing Agent: Draft & Schedule Launch Tweet...")
                thread = await marketing_agent.generate_viral_thread(f"Launching {startup.name}: {startup.description}")
                if thread and len(thread) > 0:
                     print(f"      ✅ Draft created: {thread[0][:50]}...")
                     
                     # Schedule it (Real Internal Engine)
                     print("      🤖 Scheduling to Internal Engine...")
                     res = await marketing_agent.cross_post_to_socials(
                         content=thread[0], 
                         platforms=["twitter", "linkedin"], 
                         startup_id=str(startup.id)
                     )
                     print(f"      ✅ Result: {res}")
                else:
                     print("      ❌ Failed to generate thread")
                
            except Exception as e:
                print(f"      ❌ Marketing Error: {e}")

            # 3. Trigger Sales Agent (ICP & Outreach)
            print("   🤖 Sales Agent: Defining ICP & Test Outreach...")
            
            try:
                # Force execution of outreach node logic manually to test engine
                # Use internal engine directly to prove connectivity
                from app.integrations.instantly import InstantlyIntegration
                engine = InstantlyIntegration()
                
                # We'll just "Add Lead" to the campaign as a test of the engine
                print("   🤖 Sales Agent: Adding 'Internal Tester' to Campaign...")
                res = await engine.execute_action("add_lead_to_campaign", {
                    "email": f"founders+{startup.name.lower().replace(' ', '')}@momentaic.com", # Safe test email
                    "startup_id": str(startup.id),
                    "first_name": "Internal",
                    "last_name": "Tester",
                    "campaign_id": "dogfood_campaign_01",
                    "variables": {"product": startup.name}
                })
                print(f"      ✅ Lead Queued: {res}")
                
            except Exception as e:
                 print(f"      ❌ Sales Error: {e}")

    print("\n✅ DOGFOOD LAUNCH COMPLETE. ALL AGENTS TRIGGERED.")

if __name__ == "__main__":
    asyncio.run(dogfood_launch())
