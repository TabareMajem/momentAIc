import asyncio
import sys
import os
from sqlalchemy import select

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import async_session_maker
from app.models.user import User, UserTier
from app.core.security import get_password_hash

async def ensure_user_admin():
    async with async_session_maker() as db:
        email = "tabaremajem@gmail.com"
        password = "88888888" # As requested by user
        
        # Check if exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {email} found. Updating privileges...")
            user.is_superuser = True
            user.tier = UserTier.GOD_MODE
            # Optional: Reset password to ensure access if they forgot
            # user.hashed_password = get_password_hash(password) 
        else:
            print(f"User {email} not found. Creating new Superuser...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name="Tabare Majem", # Placeholder name
                is_superuser=True,
                is_active=True,
                tier=UserTier.GOD_MODE,
                credits_balance=99999
            )
            db.add(user)
            
        await db.commit()
        print(f"✅ User {email} is ready with Superuser access.")

if __name__ == "__main__":
    asyncio.run(ensure_user_admin())
