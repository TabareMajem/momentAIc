import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import async_session_maker, init_db, engine
from app.models.integration import MarketplaceTool

from app.core.config import settings
# This script seeds initial marketplace tools
async def seed_marketplace():
    db_url = settings.database_url.replace("@postgres:", "@172.19.0.2:")
    print(f"Connecting to: {db_url}")
    
    local_engine = create_async_engine(db_url)
    
    # Initialize DB (create tables)
    async with local_engine.begin() as conn:
        await conn.run_sync(MarketplaceTool.metadata.create_all)
    
    async_session = sessionmaker(local_engine, class_=AsyncSession, expire_on_commit=False)
    
    tools = [
        {
            "name": "Slack Bridge X",
            "description": "Enterprise-grade Slack connector for real-time channel monitoring and automated messaging via MCP.",
            "icon": "💬",
            "mcp_url": "https://mcp-slack-bridge.momentaic.workers.dev/mcp",
            "category": "comms"
        },
        {
            "name": "Github Analyzer Pro",
            "description": "Deep repository insights, PR summaries, and code quality audits directly in your agent's context.",
            "icon": "🐙",
            "mcp_url": "https://mcp-github-analyzer.momentaic.workers.dev/mcp",
            "category": "devops"
        },
        {
            "name": "Notion Sync Protocol",
            "description": "Write and read from Notion databases seamlessly. Perfect for knowledge management and task tracking.",
            "icon": "📝",
            "mcp_url": "https://mcp-notion-sync.momentaic.workers.dev/mcp",
            "category": "productivity"
        },
         {
            "name": "Linear Ops Dashboard",
            "description": "Manage issues, cycles, and projects from any terminal or agent conversation.",
            "icon": "🟦",
            "mcp_url": "https://mcp-linear-ops.momentaic.workers.dev/mcp",
            "category": "devops"
        }
    ]
    
    async with async_session() as session:
        for tool_data in tools:
            # Check if exists
            from sqlalchemy import select
            q = await session.execute(select(MarketplaceTool).where(MarketplaceTool.name == tool_data["name"]))
            if q.scalar_one_or_none():
                continue
                
            tool = MarketplaceTool(
                **tool_data,
                is_vetted=True,
                total_installs=12 # Initial social proof
            )
            session.add(tool)
        await session.commit()
    print("Marketplace seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_marketplace())
