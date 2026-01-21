"""
Growth Engine Schemas
CRM (Leads) and Content Studio schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

from app.models.growth import LeadStatus, LeadSource, ContentPlatform, ContentStatus


# ==================
# Lead Schemas
# ==================

class LeadBase(BaseModel):
    """Base lead fields"""
    company_name: str = Field(..., min_length=2, max_length=255)
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_title: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_linkedin: Optional[str] = None
    contact_phone: Optional[str] = None


class LeadCreate(LeadBase):
    """Create lead request"""
    source: LeadSource = LeadSource.MANUAL
    deal_value: Optional[float] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class LeadUpdate(BaseModel):
    """Update lead request"""
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    company_industry: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_linkedin: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    deal_value: Optional[float] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    next_followup_at: Optional[datetime] = None


class LeadResponse(LeadBase):
    """Lead response"""
    id: UUID
    startup_id: UUID
    status: LeadStatus
    source: LeadSource
    probability: int
    deal_value: Optional[float]
    autopilot_enabled: bool
    research_data: Dict[str, Any]
    last_contacted_at: Optional[datetime]
    next_followup_at: Optional[datetime]
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class LeadWithMessages(LeadResponse):
    """Lead with outreach history"""
    outreach_messages: List["OutreachMessageResponse"]


class LeadKanbanResponse(BaseModel):
    """Kanban board response"""
    new: List[LeadResponse]
    researching: List[LeadResponse]
    outreach: List[LeadResponse]
    replied: List[LeadResponse]
    meeting: List[LeadResponse]
    negotiation: List[LeadResponse]
    won: List[LeadResponse]
    lost: List[LeadResponse]


class LeadAutopilotRequest(BaseModel):
    """Enable/disable autopilot"""
    enabled: bool
    max_followups: int = Field(default=3, ge=1, le=10)
    followup_interval_days: int = Field(default=3, ge=1, le=14)


# ==================
# Outreach Schemas
# ==================

class OutreachMessageCreate(BaseModel):
    """Create outreach message"""
    channel: str = Field(..., pattern="^(email|linkedin|twitter)$")
    subject: Optional[str] = None
    body: str


class OutreachMessageResponse(BaseModel):
    """Outreach message response"""
    id: UUID
    lead_id: UUID
    channel: str
    subject: Optional[str]
    body: str
    direction: str
    status: str
    ai_generated: bool
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class GenerateOutreachRequest(BaseModel):
    """Generate AI outreach"""
    channel: str = Field(..., pattern="^(email|linkedin|twitter)$")
    tone: str = Field(default="professional", pattern="^(professional|casual|friendly|bold)$")
    objective: str = Field(default="intro", pattern="^(intro|followup|demo_request|case_study)$")
    custom_context: Optional[str] = None


class GenerateOutreachResponse(BaseModel):
    """Generated outreach response"""
    subject: Optional[str]
    body: str
    hook_used: str
    personalization_points: List[str]


# ==================
# Content Schemas
# ==================

class ContentBase(BaseModel):
    """Base content fields"""
    title: str = Field(..., min_length=5, max_length=500)
    platform: ContentPlatform
    content_type: str = Field(..., pattern="^(post|thread|article|story|newsletter)$")


class ContentCreate(ContentBase):
    """Create content request"""
    body: str
    hook: Optional[str] = None
    cta: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    media_urls: List[str] = Field(default_factory=list)
    scheduled_for: Optional[datetime] = None


class ContentUpdate(BaseModel):
    """Update content request"""
    title: Optional[str] = None
    body: Optional[str] = None
    hook: Optional[str] = None
    cta: Optional[str] = None
    hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    status: Optional[ContentStatus] = None
    scheduled_for: Optional[datetime] = None


class ContentResponse(ContentBase):
    """Content response"""
    id: UUID
    startup_id: UUID
    body: str
    hook: Optional[str]
    cta: Optional[str]
    hashtags: List[str]
    media_urls: List[str]
    status: ContentStatus
    scheduled_for: Optional[datetime]
    published_at: Optional[datetime]
    published_url: Optional[str]
    ai_generated: bool
    generation_context: Dict[str, Any]
    metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class GenerateContentRequest(BaseModel):
    """Generate AI content"""
    platform: ContentPlatform
    content_type: str = Field(default="post", pattern="^(post|thread|article|story)$")
    topic: str = Field(..., min_length=5)
    tone: str = Field(default="professional", pattern="^(professional|casual|bold|educational|inspirational)$")
    include_hashtags: bool = True
    trend_based: bool = False
    custom_context: Optional[str] = None


class GenerateContentResponse(BaseModel):
    """Generated content response"""
    title: str
    hook: str
    body: str
    cta: str
    hashtags: List[str]
    trend_sources: Optional[List[str]] = None


class ContentCalendarResponse(BaseModel):
    """Content calendar view"""
    scheduled: List[ContentResponse]
    drafts: List[ContentResponse]
    published_this_week: List[ContentResponse]


# ==================
# Acquisition Schemas
# ==================

class AcquisitionChannelBase(BaseModel):
    """Base channel fields"""
    name: str = Field(..., min_length=2, max_length=100)
    channel_type: str = Field(..., pattern="^(ads|organic|social|referral|email)$")
    platform: str = Field(..., pattern="^(google|meta|twitter|linkedin|direct|other)$")
    monthly_budget: float = Field(default=0, ge=0)


class AcquisitionChannelCreate(AcquisitionChannelBase):
    """Create channel request"""
    settings: Dict[str, Any] = Field(default_factory=dict)


class AcquisitionChannelUpdate(BaseModel):
    """Update channel request"""
    name: Optional[str] = None
    channel_type: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    monthly_budget: Optional[float] = None
    settings: Optional[Dict[str, Any]] = None


class ChannelMetricResponse(BaseModel):
    """Channel metric response"""
    id: UUID
    channel_id: UUID
    date: datetime
    impressions: int
    clicks: int
    leads_count: int
    conversions_count: int
    spend: float
    revenue: float
    cac: float
    roas: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


class AcquisitionChannelResponse(AcquisitionChannelBase):
    """Channel response"""
    id: UUID
    startup_id: UUID
    status: str
    total_spend: float
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metrics: List[ChannelMetricResponse] = Field(default_factory=list)
    
    model_config = {"from_attributes": True}


class ChannelSummaryResponse(BaseModel):
    """Aggregated channel performance summary"""
    channel_id: UUID
    name: str
    total_spend: float
    total_leads: int
    total_conversions: int
    avg_cac: float
    avg_roas: float
    roi: float


# Forward references
LeadWithMessages.model_rebuild()
AcquisitionChannelResponse.model_rebuild()

class CampaignGenerateRequest(BaseModel):
    """Generate campaign request"""
    template_name: str
    template_id: str


# ==================
# Empire Builder Schemas
# ==================

class EmpireStatus(BaseModel):
    """General empire status/progress"""
    current_step: int = Field(..., ge=0, le=4)
    step_data: Dict[str, Any] = Field(default_factory=dict)
    completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class EmpireStepUpdate(BaseModel):
    """Update current empire step"""
    step: int = Field(..., ge=0, le=4)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    complete: bool = False
