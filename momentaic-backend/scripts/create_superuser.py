import asyncio
import sys
import os
from sqlalchemy import select

# Add app to path
sys.path.append(os.getcwd())

from app.core.database import async_session_maker
from app.models.user import User, UserTier
from app.core.security import get_password_hash

async def create_superuser():
    async with async_session_maker() as db:
        email = "admin@momentaic.com"
        password = "CHANGE_ME_ADMIN"
        
        # Check if exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {email} exists. Updating password...")
            user.hashed_password = get_password_hash(password)
            user.is_superuser = True
            user.is_active = True
            user.tier = UserTier.GOD_MODE
        else:
            print(f"Creating superuser {email}...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name="System Admin",
                is_superuser=True,
                is_active=True,
                tier=UserTier.GOD_MODE,
                credits_balance=99999
            )
            db.add(user)
            
        await db.commit()
        print(f"✅ Superuser ready: {email} / {password}")

if __name__ == "__main__":
    asyncio.run(create_superuser())
