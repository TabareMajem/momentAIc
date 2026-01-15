
import asyncio
import structlog
from app.core.database import async_session_maker
from app.models.user import User, UserTier
from sqlalchemy import select

logger = structlog.get_logger()

async def ensure_admin():
    email = "tabaremajem@gmail.com"
    # Pre-computed bcrypt hash for '88888888'
    hashed = "$2b$12$nMI3cLpN/8R9CjovQQ4qg.Job5eIMvUdAmHdNMQdFeOZhBlg7t206"
    
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {email} exists. Updating password...")
            user.hashed_password = hashed
            user.tier = UserTier.GOD_MODE
            user.is_superuser = True
            user.is_active = True
        else:
            print(f"Creating user {email}...")
            user = User(
                email=email,
                hashed_password=hashed,
                full_name="Tabare Majem",
                tier=UserTier.GOD_MODE,
                is_superuser=True,
                is_active=True
            )
            db.add(user)
            
        await db.commit()
        print("Admin user secured.")

if __name__ == "__main__":
    asyncio.run(ensure_admin())
