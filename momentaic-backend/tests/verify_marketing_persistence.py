
import asyncio
import structlog
import sys
import os
import uuid

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.marketing_agent import marketing_agent
from app.core.database import async_session_maker
from app.models.startup import Startup
from app.models.growth import ContentItem
from sqlalchemy import select, delete

logger = structlog.get_logger()

async def verify_persistence():
    print("--- Verifying Marketing Agent Persistence ---")
    
    # 1. Create dummy Startup
    startup_id = str(uuid.uuid4())
    print(f"Creating dummy startup: {startup_id}")
    
    async with async_session_maker() as db:
        try:
            startup = Startup(
                id=uuid.UUID(startup_id),
                name="Test Startup for Remediation",
                description="Testing DB persistence",
                owner_id=uuid.uuid4() # Random owner
            )
            db.add(startup)
            await db.commit()
            
            # 2. Call cross_post_to_socials
            print("Calling cross_post_to_socials...")
            content = "This is a test post that should be saved to DB."
            platforms = ["twitter", "linkedin"]
            
            result = await marketing_agent.cross_post_to_socials(
                content=content, 
                platforms=platforms, 
                startup_id=startup_id
            )
            
            # 3. Verify Result
            print(f"Result: {result}")
            if result.get("mode") == "persistence":
                print("✅ Success: Mode is 'persistence'")
                print(f"✅ Created {len(result.get('content_ids', []))} content items.")
            else:
                print(f"❌ Failed: Mode is {result.get('mode')}")
                
            # 4. Verify DB
            stmt = select(ContentItem).filter(ContentItem.startup_id == uuid.UUID(startup_id))
            result_db = await db.execute(stmt)
            items = result_db.scalars().all()
            
            print(f"DB Check: Found {len(items)} items in 'content_items' table.")
            for item in items:
                print(f"  - Item: {item.title} | Status: {item.status}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            await db.rollback()
        finally:
            # Cleanup
            print("Cleaning up...")
            try:
                # Need explicit delete statement
                await db.execute(delete(Startup).where(Startup.id == uuid.UUID(startup_id)))
                await db.commit()
                print("Cleanup complete.")
            except Exception as e:
                print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_persistence())
