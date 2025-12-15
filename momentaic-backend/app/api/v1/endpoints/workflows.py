"""
Agent Forge Endpoints
Workflow builder and execution engine
"""

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access, require_credits
from app.core.config import settings
from app.models.user import User
from app.models.workflow import (
    Workflow, WorkflowStatus, WorkflowRun, WorkflowRunStatus,
    WorkflowLog, LogLevel, WorkflowApproval, ApprovalStatus,
)
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowListResponse,
    AnalyzeWorkflowRequest, AnalyzeWorkflowResponse, NodeConfig, EdgeConfig,
    RunWorkflowRequest, WorkflowRunResponse, WorkflowRunWithLogs,
    WorkflowLogResponse, ApprovalResponse, ApprovalDecisionRequest,
    PendingApprovalsResponse, WebhookTriggerRequest, WebhookResponse,
)

router = APIRouter()


# ==================
# Workflow CRUD
# ==================

@router.get("/workflows", response_model=List[WorkflowListResponse])
async def list_workflows(
    startup_id: UUID,
    status: Optional[WorkflowStatus] = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List workflows for a startup.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    query = select(Workflow).where(Workflow.startup_id == startup_id)
    
    if status:
        query = query.where(Workflow.status == status)
    
    query = query.order_by(Workflow.updated_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    response = []
    for wf in workflows:
        # Get last run
        run_result = await db.execute(
            select(WorkflowRun)
            .where(WorkflowRun.workflow_id == wf.id)
            .order_by(WorkflowRun.created_at.desc())
            .limit(1)
        )
        last_run = run_result.scalar_one_or_none()
        
        response.append(WorkflowListResponse(
            id=wf.id,
            name=wf.name,
            description=wf.description,
            status=wf.status,
            trigger_type=wf.trigger_type,
            run_count=wf.run_count,
            success_count=wf.success_count,
            last_run_at=last_run.created_at if last_run else None,
            created_at=wf.created_at,
        ))
    
    return response


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    startup_id: UUID,
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new workflow.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    # Generate webhook URL if webhook trigger
    webhook_url = None
    if workflow_data.trigger_type == "webhook":
        webhook_url = f"wh_{uuid4().hex[:16]}"
    
    workflow = Workflow(
        startup_id=startup_id,
        name=workflow_data.name,
        description=workflow_data.description,
        nodes=[n.model_dump() for n in workflow_data.nodes],
        edges=[e.model_dump() for e in workflow_data.edges],
        trigger_type=workflow_data.trigger_type,
        trigger_config=workflow_data.trigger_config or {},
        webhook_url=webhook_url,
    )
    
    db.add(workflow)
    await db.flush()
    
    return WorkflowResponse.model_validate(workflow)


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    startup_id: UUID,
    workflow_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a workflow by ID.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.startup_id == startup_id
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return WorkflowResponse.model_validate(workflow)


@router.patch("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    startup_id: UUID,
    workflow_id: UUID,
    workflow_update: WorkflowUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a workflow.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.startup_id == startup_id
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    update_data = workflow_update.model_dump(exclude_unset=True)
    
    # Handle nodes and edges specially
    if "nodes" in update_data and update_data["nodes"]:
        update_data["nodes"] = [n.model_dump() if hasattr(n, 'model_dump') else n for n in update_data["nodes"]]
    if "edges" in update_data and update_data["edges"]:
        update_data["edges"] = [e.model_dump() if hasattr(e, 'model_dump') else e for e in update_data["edges"]]
    
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    return WorkflowResponse.model_validate(workflow)


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    startup_id: UUID,
    workflow_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a workflow.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.startup_id == startup_id
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    await db.delete(workflow)


# ==================
# Workflow Analysis
# ==================

@router.post("/analyze", response_model=AnalyzeWorkflowResponse)
async def analyze_workflow(
    startup_id: UUID,
    analyze_request: AnalyzeWorkflowRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze natural language prompt and generate workflow DAG.
    
    Uses LLM to understand user intent and create node/edge structure.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    from app.agents.base import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    from app.models.workflow import NodeType
    
    llm = get_llm("gemini-pro")
    
    if not llm:
        # Mock response
        return AnalyzeWorkflowResponse(
            understanding=f"I understand you want to: {analyze_request.prompt}",
            suggested_nodes=[
                NodeConfig(id="trigger_1", type=NodeType.TRIGGER, label="Start", config={}),
                NodeConfig(id="ai_1", type=NodeType.AI, label="Process", config={"model": "gemini-pro"}),
                NodeConfig(id="notify_1", type=NodeType.NOTIFICATION, label="Notify", config={}),
            ],
            suggested_edges=[
                EdgeConfig(id="e1", source="trigger_1", target="ai_1"),
                EdgeConfig(id="e2", source="ai_1", target="notify_1"),
            ],
            required_integrations=[],
            estimated_credits=5,
            warnings=[],
        )
    
    prompt = f"""Analyze this workflow request and design a DAG (Directed Acyclic Graph).

User Request: {analyze_request.prompt}
{f"Additional Context: {analyze_request.context}" if analyze_request.context else ""}

Available node types:
- trigger: Start the workflow (manual, webhook, schedule)
- ai: AI processing (summarize, analyze, generate)
- http: Make HTTP requests
- browser: Web scraping/automation
- code: Run custom code
- human: Human-in-the-loop approval
- condition: Branching logic
- loop: Iterate over items
- transform: Data transformation
- notification: Send notifications

Design the workflow with:
1. Clear understanding of user intent
2. Logical sequence of nodes
3. Appropriate connections (edges)
4. Required integrations
5. Any warnings or considerations

Format response as:
UNDERSTANDING: [your understanding]
NODES:
- id: [id], type: [type], label: [label], config: [json config]
EDGES:
- source: [source_id], target: [target_id]
INTEGRATIONS: [list]
WARNINGS: [list]
CREDITS: [estimated number]"""
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content="You are a workflow automation expert."),
            HumanMessage(content=prompt),
        ])
        
        # Parse response (simplified)
        import re
        
        understanding = ""
        nodes = []
        edges = []
        integrations = []
        warnings = []
        credits = 5
        
        understanding_match = re.search(r"UNDERSTANDING:\s*(.+?)(?=NODES:|$)", response.content, re.DOTALL)
        if understanding_match:
            understanding = understanding_match.group(1).strip()
        
        # Parse nodes
        node_section = re.search(r"NODES:(.*?)(?=EDGES:|$)", response.content, re.DOTALL)
        if node_section:
            node_lines = re.findall(r"-\s*id:\s*(\w+),\s*type:\s*(\w+),\s*label:\s*(.+?)(?:,\s*config:\s*(\{.*?\}))?(?:\n|$)", node_section.group(1))
            for i, (nid, ntype, nlabel, nconfig) in enumerate(node_lines):
                try:
                    node_type = NodeType(ntype.lower())
                except:
                    node_type = NodeType.AI
                
                nodes.append(NodeConfig(
                    id=nid or f"node_{i}",
                    type=node_type,
                    label=nlabel.strip(),
                    config={"raw": nconfig} if nconfig else {},
                ))
        
        # Parse edges
        edge_section = re.search(r"EDGES:(.*?)(?=INTEGRATIONS:|$)", response.content, re.DOTALL)
        if edge_section:
            edge_lines = re.findall(r"-\s*source:\s*(\w+),\s*target:\s*(\w+)", edge_section.group(1))
            for i, (source, target) in enumerate(edge_lines):
                edges.append(EdgeConfig(
                    id=f"edge_{i}",
                    source=source,
                    target=target,
                ))
        
        # Default nodes if none parsed
        if not nodes:
            nodes = [
                NodeConfig(id="trigger_1", type=NodeType.TRIGGER, label="Start"),
                NodeConfig(id="process_1", type=NodeType.AI, label="Process"),
            ]
            edges = [EdgeConfig(id="e1", source="trigger_1", target="process_1")]
        
        return AnalyzeWorkflowResponse(
            understanding=understanding or f"Workflow to: {analyze_request.prompt}",
            suggested_nodes=nodes,
            suggested_edges=edges,
            required_integrations=integrations,
            estimated_credits=credits,
            warnings=warnings,
        )
        
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Workflow analysis error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# ==================
# Workflow Execution
# ==================

@router.post("/workflows/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(
    startup_id: UUID,
    workflow_id: UUID,
    run_request: RunWorkflowRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_credits(settings.credit_cost_forge_run, "Workflow execution")),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a workflow.
    
    Costs 10 credits per run.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.startup_id == startup_id
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if workflow.status != WorkflowStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow is not active (status: {workflow.status.value})"
        )
    
    # Create run record
    run = WorkflowRun(
        workflow_id=workflow_id,
        status=WorkflowRunStatus.PENDING,
        inputs=run_request.inputs,
    )
    
    db.add(run)
    await db.flush()
    
    # Update workflow stats
    workflow.run_count += 1
    
    if run_request.async_execution:
        # Queue for background execution
        background_tasks.add_task(
            execute_workflow_task,
            run_id=str(run.id),
            workflow_id=str(workflow_id),
        )
        run.status = WorkflowRunStatus.RUNNING
        run.started_at = datetime.utcnow()
    else:
        # Synchronous execution (simplified)
        run.status = WorkflowRunStatus.RUNNING
        run.started_at = datetime.utcnow()
        
        try:
            # Execute nodes
            context = dict(run_request.inputs)
            
            for node in workflow.nodes:
                # Log execution
                log = WorkflowLog(
                    run_id=run.id,
                    node_id=node.get("id"),
                    level=LogLevel.INFO,
                    message=f"Executing node: {node.get('label', node.get('id'))}",
                )
                db.add(log)
                
                run.current_node_id = node.get("id")
                
                # Simulate node execution
                context[f"{node.get('id')}_output"] = f"Processed by {node.get('type')}"
            
            run.status = WorkflowRunStatus.COMPLETED
            run.completed_at = datetime.utcnow()
            run.outputs = context
            workflow.success_count += 1
            
        except Exception as e:
            run.status = WorkflowRunStatus.FAILED
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
    
    return WorkflowRunResponse.model_validate(run)


async def execute_workflow_task(run_id: str, workflow_id: str):
    """
    Background task for workflow execution.
    """
    import structlog
    logger = structlog.get_logger()
    
    logger.info("Executing workflow", run_id=run_id, workflow_id=workflow_id)
    
    # In production, use Celery for proper background task execution
    # This is a simplified async execution
    import asyncio
    await asyncio.sleep(2)  # Simulate work
    
    logger.info("Workflow completed", run_id=run_id)


@router.get("/workflows/{workflow_id}/runs", response_model=List[WorkflowRunResponse])
async def list_workflow_runs(
    startup_id: UUID,
    workflow_id: UUID,
    status: Optional[WorkflowRunStatus] = None,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List runs for a workflow.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    query = (
        select(WorkflowRun)
        .join(Workflow)
        .where(
            WorkflowRun.workflow_id == workflow_id,
            Workflow.startup_id == startup_id
        )
    )
    
    if status:
        query = query.where(WorkflowRun.status == status)
    
    query = query.order_by(WorkflowRun.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    runs = result.scalars().all()
    
    return [WorkflowRunResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=WorkflowRunWithLogs)
async def get_workflow_run(
    startup_id: UUID,
    run_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a workflow run with its logs.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(WorkflowRun)
        .options(selectinload(WorkflowRun.logs))
        .join(Workflow)
        .where(
            WorkflowRun.id == run_id,
            Workflow.startup_id == startup_id
        )
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found"
        )
    
    return WorkflowRunWithLogs.model_validate(run)


# ==================
# Approvals
# ==================

@router.get("/approvals/pending", response_model=PendingApprovalsResponse)
async def get_pending_approvals(
    startup_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all pending approval requests.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(WorkflowApproval)
        .join(WorkflowRun)
        .join(Workflow)
        .where(
            Workflow.startup_id == startup_id,
            WorkflowApproval.status == ApprovalStatus.PENDING
        )
        .order_by(WorkflowApproval.created_at.desc())
    )
    approvals = result.scalars().all()
    
    return PendingApprovalsResponse(
        total=len(approvals),
        approvals=[ApprovalResponse.model_validate(a) for a in approvals],
    )


@router.post("/approvals/{approval_id}/decide", response_model=ApprovalResponse)
async def decide_approval(
    startup_id: UUID,
    approval_id: UUID,
    decision: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a decision for an approval request.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(WorkflowApproval)
        .join(WorkflowRun)
        .join(Workflow)
        .where(
            WorkflowApproval.id == approval_id,
            Workflow.startup_id == startup_id
        )
    )
    approval = result.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval already processed (status: {approval.status.value})"
        )
    
    approval.status = ApprovalStatus.APPROVED if decision.decision == "approved" else ApprovalStatus.REJECTED
    approval.decision_by = current_user.id
    approval.decision_feedback = decision.feedback
    approval.decided_at = datetime.utcnow()
    
    # If approved, resume workflow execution
    if approval.status == ApprovalStatus.APPROVED:
        run_result = await db.execute(
            select(WorkflowRun).where(WorkflowRun.id == approval.run_id)
        )
        run = run_result.scalar_one()
        run.status = WorkflowRunStatus.RUNNING
        # In production, trigger continuation of workflow
    
    return ApprovalResponse.model_validate(approval)


# ==================
# Webhooks
# ==================

@router.post("/webhook/{webhook_url}", response_model=WebhookResponse)
async def trigger_webhook(
    webhook_url: str,
    trigger_request: WebhookTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a workflow via webhook.
    
    Public endpoint - no authentication required.
    """
    result = await db.execute(
        select(Workflow).where(
            Workflow.webhook_url == webhook_url,
            Workflow.status == WorkflowStatus.ACTIVE
        )
    )
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found or workflow not active"
        )
    
    # Create run
    run = WorkflowRun(
        workflow_id=workflow.id,
        status=WorkflowRunStatus.PENDING,
        inputs=trigger_request.data,
    )
    
    db.add(run)
    await db.flush()
    
    workflow.run_count += 1
    
    # Queue execution
    background_tasks.add_task(
        execute_workflow_task,
        run_id=str(run.id),
        workflow_id=str(workflow.id),
    )
    
    run.status = WorkflowRunStatus.RUNNING
    run.started_at = datetime.utcnow()
    
    return WebhookResponse(
        run_id=run.id,
        status="started",
        message="Workflow execution started",
    )
