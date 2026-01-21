from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class AgentForgeEventType(str, Enum):
    WORKFLOW_START = "WORKFLOW_START"
    NODE_COMPLETED = "NODE_COMPLETED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"

class AgentForgeWebhookPayload(BaseModel):
    event: AgentForgeEventType
    workflow_id: str
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Context
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
