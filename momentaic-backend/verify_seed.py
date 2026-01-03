import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.integration import MarketplaceTool

async def verify_seeding():
    db_url = settings.database_url.replace("@postgres:", "@172.19.0.2:")
    print(f"Connecting to: {db_url}")
    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(MarketplaceTool))
        tools = result.scalars().all()
        print(f"Found {len(tools)} tools in marketplace.")
        for tool in tools:
            print(f"- {tool.name} (Vetted: {tool.is_vetted}, Category: {tool.category})")

if __name__ == "__main__":
    asyncio.run(verify_seeding())
