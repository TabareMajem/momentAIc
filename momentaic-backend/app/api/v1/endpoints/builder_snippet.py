"""
Integration Builder Snippet
Provides a direct chat interface to the Integration Builder Agent.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


class BuilderChatRequest(BaseModel):
    message: str


@router.post("/builder/chat")
async def chat_builder(
    request: BuilderChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Direct line to the Integration Builder Agent.
    Generates real Python connector code.
    """
    from app.agents.integration_builder_agent import integration_builder_agent

    # 1. Process with Agent
    result = await integration_builder_agent.process(
        message=request.message,
        user_id=str(current_user.id)
    )

    # 2. Return result with file URL
    return {
        "response": result.get("response", "Code generated."),
        "file_url": result.get("file_url")
    }
