import asyncio
import sys
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user import User, UserTier
from app.core.security import get_password_hash

async def create_admin(email, password, name):
    async with async_session_maker() as session:
        # Check if user exists
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User {email} already exists. Updating to admin...")
            user.is_superuser = True
            user.hashed_password = get_password_hash(password)
            user.full_name = name
            user.tier = UserTier.GOD_MODE
        else:
            print(f"Creating new admin user {email}...")
            user = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=name,
                is_superuser=True,
                tier=UserTier.GOD_MODE,
                credits_balance=999999
            )
            session.add(user)
        
        await session.commit()
        print("Admin user created/updated successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [name]")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else "Admin User"
    
    asyncio.run(create_admin(email, password, name))
