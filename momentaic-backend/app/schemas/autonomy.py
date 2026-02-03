"""
Autonomy Settings Schemas
Pydantic models for proactive agent configuration
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AutonomySettingsBase(BaseModel):
    """Base schema for autonomy settings"""
    global_level: int = Field(1, ge=0, le=3, description="Global autonomy level (0-3)")
    marketing_level: Optional[int] = Field(None, ge=0, le=3)
    sales_level: Optional[int] = Field(None, ge=0, le=3)
    finance_level: Optional[int] = Field(None, ge=0, le=3)
    content_level: Optional[int] = Field(None, ge=0, le=3)
    competitive_level: Optional[int] = Field(None, ge=0, le=3)
    daily_action_limit: int = Field(50, ge=1, le=500)
    daily_spend_limit_usd: float = Field(100.0, ge=0, le=10000)
    is_paused: bool = False
    paused_reason: Optional[str] = None
    notify_on_action: bool = True
    notify_channel: str = "email"


class AutonomySettingsCreate(AutonomySettingsBase):
    """Create autonomy settings"""
    pass


class AutonomySettingsUpdate(BaseModel):
    """Update autonomy settings (all fields optional)"""
    global_level: Optional[int] = Field(None, ge=0, le=3)
    marketing_level: Optional[int] = Field(None, ge=0, le=3)
    sales_level: Optional[int] = Field(None, ge=0, le=3)
    finance_level: Optional[int] = Field(None, ge=0, le=3)
    content_level: Optional[int] = Field(None, ge=0, le=3)
    competitive_level: Optional[int] = Field(None, ge=0, le=3)
    daily_action_limit: Optional[int] = Field(None, ge=1, le=500)
    daily_spend_limit_usd: Optional[float] = Field(None, ge=0, le=10000)
    is_paused: Optional[bool] = None
    paused_reason: Optional[str] = None
    notify_on_action: Optional[bool] = None
    notify_channel: Optional[str] = None


class AutonomySettingsResponse(AutonomySettingsBase):
    """Response schema for autonomy settings"""
    id: UUID
    startup_id: UUID
    paused_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProactiveActionResponse(BaseModel):
    """Response schema for proactive action log"""
    id: UUID
    startup_id: UUID
    agent_type: str
    action_type: str
    category: str
    title: str
    description: Optional[str]
    status: str
    autonomy_level_used: int
    executed_at: Optional[datetime]
    requires_approval: bool
    is_reversible: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
