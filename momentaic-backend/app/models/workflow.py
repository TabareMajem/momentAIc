"""
Agent Forge Models
Workflow builder and execution engine - inspired by AgentForge
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.core.database import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow definition status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class WorkflowRunStatus(str, enum.Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(str, enum.Enum):
    """Workflow node types - matching AgentForge"""
    TRIGGER = "trigger"
    AI = "ai"
    HTTP = "http"
    BROWSER = "browser"
    CODE = "code"
    HUMAN = "human"
    CONDITION = "condition"
    LOOP = "loop"
    TRANSFORM = "transform"
    NOTIFICATION = "notification"


class Workflow(Base):
    """Workflow definition - the DAG structure"""
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    startup_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False
    )
    
    # Workflow Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # The DAG Definition (JSON)
    nodes: Mapped[List[dict]] = mapped_column(JSONB, default=list)
    """
    Example node structure:
    {
        "id": "node_1",
        "type": "ai",
        "label": "Research Lead",
        "config": {
            "model": "gemini-pro",
            "prompt_template": "Research {company_name}...",
            "tools": ["web_search", "linkedin_search"]
        },
        "position": {"x": 100, "y": 100}
    }
    """
    
    edges: Mapped[List[dict]] = mapped_column(JSONB, default=list)
    """
    Example edge structure:
    {
        "id": "edge_1",
        "source": "node_1",
        "target": "node_2",
        "condition": null  # or {"field": "status", "operator": "eq", "value": "success"}
    }
    """
    
    # Trigger Configuration
    trigger_type: Mapped[str] = mapped_column(String(50), default="manual")  # manual, webhook, schedule, event
    trigger_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    
    # Status
    status: Mapped[WorkflowStatus] = mapped_column(
        SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT
    )
    
    # Stats
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    startup: Mapped["Startup"] = relationship("Startup", back_populates="workflows")
    runs: Mapped[List["WorkflowRun"]] = relationship(
        "WorkflowRun", back_populates="workflow", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_workflows_startup", "startup_id"),
        Index("ix_workflows_webhook", "webhook_url"),
    )


class WorkflowRun(Base):
    """Individual workflow execution instance"""
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    
    # Execution State
    status: Mapped[WorkflowRunStatus] = mapped_column(
        SQLEnum(WorkflowRunStatus), default=WorkflowRunStatus.PENDING
    )
    current_node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Input/Output
    inputs: Mapped[dict] = mapped_column(JSONB, default=dict)
    outputs: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Execution Context (passed between nodes)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Error Info
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="runs")
    logs: Mapped[List["WorkflowLog"]] = relationship(
        "WorkflowLog", back_populates="run", cascade="all, delete-orphan"
    )
    approvals: Mapped[List["WorkflowApproval"]] = relationship(
        "WorkflowApproval", back_populates="run", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_workflow_runs_workflow_status", "workflow_id", "status"),
    )


class LogLevel(str, enum.Enum):
    """Log entry levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class WorkflowLog(Base):
    """Execution logs for workflow runs"""
    __tablename__ = "workflow_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    
    # Log Entry
    node_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    level: Mapped[LogLevel] = mapped_column(SQLEnum(LogLevel), default=LogLevel.INFO)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    run: Mapped["WorkflowRun"] = relationship("WorkflowRun", back_populates="logs")

    __table_args__ = (
        Index("ix_workflow_logs_run_timestamp", "run_id", "timestamp"),
    )


class ApprovalStatus(str, enum.Enum):
    """Human approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class WorkflowApproval(Base):
    """Human-in-the-loop approval requests"""
    __tablename__ = "workflow_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    
    # Approval Info
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    node_label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Content for Review
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    # Example: {"email_subject": "...", "email_body": "...", "recipient": "..."}
    
    # Status
    status: Mapped[ApprovalStatus] = mapped_column(
        SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING
    )
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, urgent
    
    # Decision
    decision_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    decision_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    run: Mapped["WorkflowRun"] = relationship("WorkflowRun", back_populates="approvals")

    __table_args__ = (
        Index("ix_workflow_approvals_status", "status"),
    )


# Forward reference
from app.models.startup import Startup
