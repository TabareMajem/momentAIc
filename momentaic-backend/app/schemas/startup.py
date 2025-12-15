"""
Startup Domain Schemas
Pydantic models for startup management
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID

from app.models.startup import StartupStage


# ==================
# Startup Schemas
# ==================

class StartupBase(BaseModel):
    """Base startup fields"""
    name: str = Field(..., min_length=2, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    industry: str = Field(..., min_length=2, max_length=100)
    stage: StartupStage = StartupStage.IDEA


class StartupCreate(StartupBase):
    """Create startup request"""
    github_repo: Optional[str] = None
    website_url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class StartupUpdate(BaseModel):
    """Update startup request"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[StartupStage] = None
    github_repo: Optional[str] = None
    website_url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class StartupResponse(StartupBase):
    """Startup response"""
    id: UUID
    owner_id: UUID
    github_repo: Optional[str]
    website_url: Optional[str]
    metrics: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class StartupDashboard(BaseModel):
    """Startup dashboard with aggregated data"""
    startup: StartupResponse
    latest_signal: Optional["SignalResponse"] = None
    active_sprint: Optional["SprintResponse"] = None
    lead_summary: Dict[str, int]  # {"new": 5, "outreach": 3, ...}
    content_scheduled: int
    recent_activity: List[Dict[str, Any]]


class MetricsUpdate(BaseModel):
    """Update startup metrics"""
    mrr: Optional[float] = None
    dau: Optional[int] = None
    wau: Optional[int] = None
    mau: Optional[int] = None
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    nps: Optional[float] = None
    churn_rate: Optional[float] = None
    cac: Optional[float] = None
    ltv: Optional[float] = None
    custom: Optional[Dict[str, Any]] = None


# ==================
# Signal Schemas
# ==================

class SignalResponse(BaseModel):
    """Neural Signal response"""
    id: UUID
    startup_id: UUID
    tech_velocity: float
    pmf_score: float
    growth_momentum: float
    runway_health: float
    overall_score: float
    ai_insights: Optional[str]
    recommendations: List[str]
    raw_data: Dict[str, Any]
    calculated_at: datetime
    
    model_config = {"from_attributes": True}


class SignalRecalcRequest(BaseModel):
    """Force signal recalculation"""
    include_github: bool = True
    include_metrics: bool = True
    include_activity: bool = True


# ==================
# Sprint Schemas
# ==================

class SprintBase(BaseModel):
    """Base sprint fields"""
    goal: str = Field(..., min_length=10)
    key_results: List[str] = Field(default_factory=list)
    start_date: date
    end_date: date


class SprintCreate(SprintBase):
    """Create sprint request"""
    pass


class SprintUpdate(BaseModel):
    """Update sprint request"""
    goal: Optional[str] = None
    key_results: Optional[List[str]] = None
    status: Optional[str] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    completed_results: Optional[List[str]] = None


class SprintResponse(SprintBase):
    """Sprint response"""
    id: UUID
    startup_id: UUID
    status: str
    progress_percentage: int
    completed_results: List[str]
    ai_feedback: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SprintWithStandups(SprintResponse):
    """Sprint with standup history"""
    standups: List["StandupResponse"]


# ==================
# Standup Schemas
# ==================

class StandupCreate(BaseModel):
    """Create standup request"""
    yesterday: str = Field(..., min_length=10)
    today: str = Field(..., min_length=10)
    blockers: Optional[str] = None
    mood: Optional[str] = Field(None, pattern="^(great|good|meh|struggling)$")


class StandupResponse(BaseModel):
    """Standup response"""
    id: UUID
    sprint_id: UUID
    yesterday: str
    today: str
    blockers: Optional[str]
    mood: Optional[str]
    alignment_score: Optional[float]
    ai_feedback: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Forward references
SignalResponse.model_rebuild()
SprintResponse.model_rebuild()
StandupResponse.model_rebuild()
StartupDashboard.model_rebuild()
SprintWithStandups.model_rebuild()
