
import sys
import os
import asyncio
import structlog

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.growth import growth_agent
from app.agents.product import product_agent
from app.agents.operations import operations_agent

logger = structlog.get_logger()

async def verify_agents():
    print("✅ Verifying GrowthSuperAgent...")
    if growth_agent and growth_agent.graph:
        print("   GrowthSuperAgent initialized successfully.")
    else:
        print("❌ GrowthSuperAgent failed to initialize.")

    print("✅ Verifying ProductSuperAgent...")
    if product_agent and product_agent.graph:
        print("   ProductSuperAgent initialized successfully.")
    else:
        print("❌ ProductSuperAgent failed to initialize.")

    print("✅ Verifying OperationsSuperAgent...")
    if operations_agent and operations_agent.graph:
        print("   OperationsSuperAgent initialized successfully.")
    else:
        print("❌ OperationsSuperAgent failed to initialize.")

if __name__ == "__main__":
    asyncio.run(verify_agents())
