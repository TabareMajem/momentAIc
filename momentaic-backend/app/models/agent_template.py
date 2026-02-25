"""
Agent Marketplace Template Model
Stores community-submitted system prompts and agent configurations.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, Text
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class AgentTemplate(Base):
    """
    Community-driven agent configurations for the Marketplace.
    """
    __tablename__ = "agent_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # The actual prompt template
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Author information (can be null if system-provided)
    author_name: Mapped[str] = mapped_column(String(100), default="MomentAIc Team")
    
    # Organization/Categorization
    industry: Mapped[str] = mapped_column(String(100), default="General")
    agent_type_target: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. "ContentAgent"
    
    # Social Proof
    upvotes: Mapped[int] = mapped_column(Integer, default=0)
    clones: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
