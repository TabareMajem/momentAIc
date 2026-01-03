import asyncio
import sys
import os
from sqlalchemy import select

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import async_session_maker
from app.models.user import User, UserTier

async def promote_user():
    async with async_session_maker() as db:
        email = "tabaremajem@gmail.com"
        
        # Check if exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {email} found.")
            if not user.is_superuser:
                print(f"Promoting {email} to Superuser...")
                user.is_superuser = True
                user.tier = UserTier.GOD_MODE # Give them full features too
                await db.commit()
                print(f"✅ {email} is now a Superuser with God Mode.")
            else:
                print(f"✅ {email} is already a Superuser.")
        else:
            print(f"❌ User {email} not found. Please sign up first.")

if __name__ == "__main__":
    asyncio.run(promote_user())
