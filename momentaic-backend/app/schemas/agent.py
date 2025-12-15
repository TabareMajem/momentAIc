"""
Agent Swarm & Conversation Schemas
Multi-agent chat system schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

from app.models.conversation import AgentType, MessageRole


# ==================
# Conversation Schemas
# ==================

class ConversationCreate(BaseModel):
    """Create conversation request"""
    agent_type: AgentType = AgentType.SUPERVISOR
    title: Optional[str] = None
    initial_context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    startup_id: UUID
    user_id: UUID
    title: Optional[str]
    agent_type: AgentType
    is_active: bool
    message_count: int
    context: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationResponse):
    """Conversation with message history"""
    messages: List["MessageResponse"]


class ConversationListResponse(BaseModel):
    """Conversation list item"""
    id: UUID
    title: Optional[str]
    agent_type: AgentType
    message_count: int
    last_message_preview: Optional[str] = None
    updated_at: datetime


# ==================
# Message Schemas
# ==================

class MessageCreate(BaseModel):
    """Send message request"""
    content: str = Field(..., min_length=1)
    agent_type: Optional[AgentType] = None  # Override conversation default


class MessageResponse(BaseModel):
    """Message response"""
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    agent_type: Optional[AgentType]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class StreamingMessageChunk(BaseModel):
    """Streaming message chunk"""
    chunk: str
    agent_type: Optional[AgentType] = None
    tool_call: Optional[Dict[str, Any]] = None
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None


# ==================
# Agent Chat Schemas
# ==================

class AgentChatRequest(BaseModel):
    """Direct agent chat request"""
    message: str = Field(..., min_length=1)
    agent_type: AgentType = AgentType.SUPERVISOR
    startup_id: UUID
    conversation_id: Optional[UUID] = None
    stream: bool = False
    include_context: bool = True


class AgentChatResponse(BaseModel):
    """Agent chat response"""
    conversation_id: UUID
    message_id: UUID
    response: str
    agent_type: AgentType
    routed_to: Optional[AgentType] = None  # If supervisor routed
    tool_calls: List[Dict[str, Any]]
    credits_used: int
    metadata: Dict[str, Any]


class AgentInfoResponse(BaseModel):
    """Agent information"""
    type: AgentType
    name: str
    description: str
    capabilities: List[str]
    available_tools: List[str]


class AvailableAgentsResponse(BaseModel):
    """List of available agents"""
    agents: List[AgentInfoResponse]


# ==================
# Tool Schemas
# ==================

class ToolCallRequest(BaseModel):
    """Tool execution request"""
    tool_name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """Tool execution response"""
    tool_name: str
    result: Any
    success: bool
    error: Optional[str] = None
    execution_time_ms: int


# ==================
# Memory Schemas
# ==================

class AgentMemoryResponse(BaseModel):
    """Agent memory item"""
    id: UUID
    agent_type: AgentType
    memory_type: str
    content: str
    importance: float
    access_count: int
    created_at: datetime
    last_accessed_at: datetime
    
    model_config = {"from_attributes": True}


class AgentMemoryCreate(BaseModel):
    """Create agent memory"""
    memory_type: str = Field(..., pattern="^(fact|preference|context|summary)$")
    content: str
    importance: int = Field(default=5, ge=1, le=10)


# ==================
# Vision Portal Schemas
# ==================

class VisionPortalRequest(BaseModel):
    """Vision Portal code generation request"""
    app_description: str = Field(..., min_length=20)
    tech_stack: Optional[str] = Field(default="react_node")
    include_user_stories: bool = True
    include_database_schema: bool = True
    include_api_spec: bool = True


class VisionPortalResponse(BaseModel):
    """Vision Portal generation response"""
    project_name: str
    user_stories: Optional[List[Dict[str, Any]]] = None
    database_schema: Optional[str] = None
    api_specification: Optional[Dict[str, Any]] = None
    generated_files: List[Dict[str, str]]  # {"path": "...", "content": "..."}
    architecture_diagram: Optional[str] = None
    next_steps: List[str]
    credits_used: int


class VisionPortalStatusResponse(BaseModel):
    """Vision Portal generation status"""
    task_id: str
    status: str
    progress: int
    current_step: str
    estimated_remaining_seconds: Optional[int] = None


# Forward references
ConversationWithMessages.model_rebuild()
