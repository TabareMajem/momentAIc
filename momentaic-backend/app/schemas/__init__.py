"""
MomentAIc API Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import List, Any, Optional

from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenPair,
    AuthResponse,
    RefreshTokenRequest,
    UpdateProfileRequest,
    CreditBalanceResponse,
    CreditTransactionResponse,
    OAuthConnectRequest,
    OAuthStatusResponse,
)

from app.schemas.startup import (
    StartupCreate,
    StartupUpdate,
    StartupResponse,
    StartupDashboard,
    MetricsUpdate,
    SignalResponse,
    SignalRecalcRequest,
    SprintCreate,
    SprintUpdate,
    SprintResponse,
    SprintWithStandups,
    StandupCreate,
    StandupResponse,
)

from app.schemas.growth import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadWithMessages,
    LeadKanbanResponse,
    LeadAutopilotRequest,
    OutreachMessageCreate,
    OutreachMessageResponse,
    GenerateOutreachRequest,
    GenerateOutreachResponse,
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    GenerateContentRequest,
    GenerateContentResponse,
    ContentCalendarResponse,
)

from app.schemas.workflow import (
    NodeConfig,
    EdgeConfig,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    AnalyzeWorkflowRequest,
    AnalyzeWorkflowResponse,
    RunWorkflowRequest,
    WorkflowRunResponse,
    WorkflowRunWithLogs,
    WorkflowLogResponse,
    ApprovalResponse,
    ApprovalDecisionRequest,
    PendingApprovalsResponse,
    WebhookTriggerRequest,
    WebhookResponse,
)

from app.schemas.agent import (
    ConversationCreate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    StreamingMessageChunk,
    AgentChatRequest,
    AgentChatResponse,
    AgentInfoResponse,
    AvailableAgentsResponse,
    ToolCallRequest,
    ToolCallResponse,
    AgentMemoryResponse,
    AgentMemoryCreate,
    VisionPortalRequest,
    VisionPortalResponse,
    VisionPortalStatusResponse,
)


# Common response schemas
class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
