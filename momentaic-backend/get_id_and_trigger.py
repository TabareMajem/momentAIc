import asyncio
from app.core.database import SessionLocal
from app.models.startup import Startup
from sqlalchemy import select
from trigger_debate import trigger_war_room

async def run():
    async with SessionLocal() as db:
        startup = (await db.execute(select(Startup).limit(1))).scalar_one_or_none()
        if startup:
            print(f"Triggering for Startup: {startup.id}")
            await trigger_war_room(str(startup.id))
        else:
            print("No startups found in DB")

asyncio.run(run())
