import asyncio
import sys
import os
from sqlalchemy import select

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import async_session_maker
from app.models.user import User
from app.models.startup import Startup

async def ensure_startup():
    async with async_session_maker() as db:
        # Find admin
        result = await db.execute(select(User).where(User.email == "admin@momentaic.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Admin user not found!")
            return

        # Check startup
        result = await db.execute(select(Startup).where(Startup.owner_id == user.id))
        startup = result.scalar_one_or_none()
        
        if not startup:
            print("Creating Yokaizen startup...")
            startup = Startup(
                owner_id=user.id,
                name="Yokaizen",
                description="AI Mental Wellness Companion",
                industry="Mental Health Tech"
            )
            db.add(startup)
            await db.commit()
            print(f"✅ Created startup: {startup.name} ({startup.id})")
        else:
            print(f"✅ Startup exists: {startup.name} ({startup.id})")

if __name__ == "__main__":
    asyncio.run(ensure_startup())
