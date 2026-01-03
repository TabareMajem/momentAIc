from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access
from app.models.user import User
from app.models.integration import (
    MarketplaceTool, Integration, IntegrationProvider, IntegrationStatus
)

router = APIRouter(prefix="/marketplace", tags=["MCP Marketplace"])

# ==================
# Schemas
# ==================

class ToolSubmit(BaseModel):
    name: str
    description: str
    mcp_url: str
    icon: str = "🔌"
    category: str = "productivity"

class MarketplaceToolResponse(BaseModel):
    id: UUID
    name: str
    description: str
    icon: str
    mcp_url: str
    category: str
    is_vetted: bool
    total_installs: int
    version: str

    class Config:
        from_attributes = True

# ==================
# Endpoints
# ==================

@router.get("/tools", response_model=List[MarketplaceToolResponse])
async def list_marketplace_tools(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all vetted community tools"""
    query = select(MarketplaceTool).where(MarketplaceTool.is_vetted == True)
    if category:
        query = query.where(MarketplaceTool.category == category)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_tool(
    tool_data: ToolSubmit,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Community submission of a new MCP tool"""
    new_tool = MarketplaceTool(
        name=tool_data.name,
        description=tool_data.description,
        mcp_url=tool_data.mcp_url,
        icon=tool_data.icon,
        category=tool_data.category,
        author_id=current_user.id,
        is_vetted=False # Needs admin approval
    )
    db.add(new_tool)
    await db.flush()
    return {"message": "Tool submitted for vetting", "id": new_tool.id}

@router.post("/install/{tool_id}")
async def install_tool(
    startup_id: UUID,
    tool_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """1-Click Install a vetted community tool to a startup"""
    await verify_startup_access(startup_id, current_user, db)
    
    # Get the tool
    tool_result = await db.execute(select(MarketplaceTool).where(MarketplaceTool.id == tool_id))
    tool = tool_result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Marketplace tool not found")
    
    # Check if already installed
    existing = await db.execute(
        select(Integration).where(
            Integration.startup_id == startup_id,
            Integration.provider == IntegrationProvider.MCP,
            Integration.name == tool.name
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Tool already installed")
    
    # Create the integration
    integration = Integration(
        user_id=current_user.id,
        startup_id=startup_id,
        provider=IntegrationProvider.MCP,
        name=tool.name,
        config={"server_url": tool.mcp_url, "marketplace_id": str(tool.id)},
        status=IntegrationStatus.ACTIVE
    )
    
    db.add(integration)
    
    # Increment install count
    tool.total_installs += 1
    
    await db.flush()
    return {"message": f"Successfully installed {tool.name}", "integration_id": integration.id}
