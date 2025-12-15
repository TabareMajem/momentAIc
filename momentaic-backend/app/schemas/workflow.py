"""
Agent Forge Schemas
Workflow builder and execution schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.workflow import (
    WorkflowStatus, WorkflowRunStatus, NodeType, LogLevel, ApprovalStatus
)


# ==================
# Workflow Definition Schemas
# ==================

class NodeConfig(BaseModel):
    """Workflow node configuration"""
    id: str
    type: NodeType
    label: str
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, int]] = None


class EdgeConfig(BaseModel):
    """Workflow edge configuration"""
    id: str
    source: str
    target: str
    condition: Optional[Dict[str, Any]] = None


class WorkflowBase(BaseModel):
    """Base workflow fields"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    """Create workflow request"""
    nodes: List[NodeConfig] = Field(default_factory=list)
    edges: List[EdgeConfig] = Field(default_factory=list)
    trigger_type: str = Field(default="manual", pattern="^(manual|webhook|schedule|event)$")
    trigger_config: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    """Update workflow request"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[NodeConfig]] = None
    edges: Optional[List[EdgeConfig]] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    status: Optional[WorkflowStatus] = None


class WorkflowResponse(WorkflowBase):
    """Workflow response"""
    id: UUID
    startup_id: UUID
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    trigger_type: str
    trigger_config: Dict[str, Any]
    webhook_url: Optional[str]
    status: WorkflowStatus
    run_count: int
    success_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class WorkflowListResponse(BaseModel):
    """Workflow list item"""
    id: UUID
    name: str
    description: Optional[str]
    status: WorkflowStatus
    trigger_type: str
    run_count: int
    success_count: int
    last_run_at: Optional[datetime] = None
    created_at: datetime


# ==================
# Workflow Analysis Schemas
# ==================

class AnalyzeWorkflowRequest(BaseModel):
    """Natural language workflow analysis"""
    prompt: str = Field(..., min_length=10)
    context: Optional[str] = None


class AnalyzeWorkflowResponse(BaseModel):
    """Workflow analysis response"""
    understanding: str
    suggested_nodes: List[NodeConfig]
    suggested_edges: List[EdgeConfig]
    required_integrations: List[str]
    estimated_credits: int
    warnings: List[str]


# ==================
# Workflow Execution Schemas
# ==================

class RunWorkflowRequest(BaseModel):
    """Run workflow request"""
    inputs: Dict[str, Any] = Field(default_factory=dict)
    async_execution: bool = True


class WorkflowRunResponse(BaseModel):
    """Workflow run response"""
    id: UUID
    workflow_id: UUID
    status: WorkflowRunStatus
    current_node_id: Optional[str]
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    context: Dict[str, Any]
    error_message: Optional[str]
    error_node_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class WorkflowRunWithLogs(WorkflowRunResponse):
    """Workflow run with execution logs"""
    logs: List["WorkflowLogResponse"]


class WorkflowLogResponse(BaseModel):
    """Workflow log entry"""
    id: UUID
    run_id: UUID
    node_id: Optional[str]
    level: LogLevel
    message: str
    metadata: Dict[str, Any]
    timestamp: datetime
    
    model_config = {"from_attributes": True}


# ==================
# Approval Schemas
# ==================

class ApprovalResponse(BaseModel):
    """Approval request response"""
    id: UUID
    run_id: UUID
    node_id: str
    node_label: str
    description: str
    content: Dict[str, Any]
    status: ApprovalStatus
    priority: str
    decision_feedback: Optional[str]
    decided_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ApprovalDecisionRequest(BaseModel):
    """Submit approval decision"""
    decision: str = Field(..., pattern="^(approved|rejected)$")
    feedback: Optional[str] = None


class PendingApprovalsResponse(BaseModel):
    """Pending approvals list"""
    total: int
    approvals: List[ApprovalResponse]


# ==================
# Webhook Schemas
# ==================

class WebhookTriggerRequest(BaseModel):
    """Webhook trigger payload"""
    data: Dict[str, Any] = Field(default_factory=dict)
    headers: Optional[Dict[str, str]] = None


class WebhookResponse(BaseModel):
    """Webhook trigger response"""
    run_id: UUID
    status: str
    message: str


# Forward references
WorkflowRunWithLogs.model_rebuild()
