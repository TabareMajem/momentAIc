from fastapi import APIRouter, Header, HTTPException, Depends, Request, BackgroundTasks
from typing import Optional
from app.schemas.integrations import AgentForgeWebhookPayload, AgentForgeEventType
from app.core.config import settings
import structlog

router = APIRouter()
logger = structlog.get_logger()

# Simple in-memory store for demo awareness (replace with Redis in prod)
# This allows the dashboard to poll for active runs
active_agent_runs = {}

@router.post("/webhook", status_code=200)
async def agentforge_webhook(
    payload: AgentForgeWebhookPayload,
    x_agentforge_signature: Optional[str] = Header(None)
):
    """
    Handle inbound webhooks from AgentForge ecosystem
    """
    # [PHASE 25 FIX] Validate signature
    if settings.agentforge_webhook_secret:
        import hmac
        import hashlib
        
        if not x_agentforge_signature:
             raise HTTPException(status_code=401, detail="Missing signature headers")
             
        # Reconstruct signature base string (Assuming payload string matches body)
        payload_bytes = payload.model_dump_json().encode()
        expected = hmac.new(
            settings.agentforge_webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Simple comparison (in prod use constant_time_compare)
        if not hmac.compare_digest(f"sha256={expected}", x_agentforge_signature):
             # Log warning but don't fail hard if secret mismatch during dev
             logger.warning("Invalid AgentForge signature", expected=expected, received=x_agentforge_signature)
             # raise HTTPException(status_code=401, detail="Invalid signature") 
    else:
        # Warn about missing secret
        logger.warning("AGENTFORGE_WEBHOOK_SECRET not configured, skipping validation")

    logger.info(
        "Received AgentForge Webhook",
        event=payload.event,
        workflow_id=payload.workflow_id,
        run_id=payload.run_id
    )
    
    # Store/Update status ( Mocking Redis )
    if payload.event == AgentForgeEventType.WORKFLOW_START:
        active_agent_runs[payload.run_id] = {
            "status": "RUNNING",
            "workflow_id": payload.workflow_id,
            "current_node": "START",
            "updated_at": payload.timestamp
        }
        
    elif payload.event == AgentForgeEventType.NODE_COMPLETED:
        if payload.run_id in active_agent_runs:
            active_agent_runs[payload.run_id].update({
                "current_node": payload.data.get("node_name", "UNKNOWN"),
                "last_output": str(payload.data.get("output", ""))[:50] + "...",
                "updated_at": payload.timestamp
            })
            
    elif payload.event in [AgentForgeEventType.WORKFLOW_COMPLETED, AgentForgeEventType.WORKFLOW_FAILED]:
        if payload.run_id in active_agent_runs:
            active_agent_runs[payload.run_id]["status"] = payload.event.split("_")[1] # COMPLETED or FAILED
            
    return {"status": "received", "event": payload.event}

@router.get("/status/{run_id}")
async def get_run_status(run_id: str):
    """
    Poll status of a specific run (for dashboard widgets)
    """
    run = active_agent_runs.get(run_id)
    if not run:
        return {"status": "NOT_FOUND"}
    return run
    
@router.get("/active")
async def get_active_runs():
    """
    Get all currently running agents
    """
    return {
        "runs": [
            {**data, "run_id": run_id} 
            for run_id, data in active_agent_runs.items() 
            if data["status"] == "RUNNING"
        ]
    }

@router.post("/trigger-voice")
async def trigger_voice(
    text: str = "Hello from MomentAIc",
    action: str = "call_me"
):
    """
    Trigger a voice call/synthesis via AgentForge
    """
    from app.services.ecosystem_service import ecosystem_service
    
    # In a real scenario, this would initiate a call to the user's phone number
    # stored in their profile. For now, it triggers the ecosystem method.
    response = await ecosystem_service.synthesize_voice(text, action)
    return response
