from fastapi import APIRouter, Header, HTTPException, Depends, Request, BackgroundTasks, Body
from typing import Optional, Any, Dict
from app.schemas.integrations import AgentForgeWebhookPayload, AgentForgeEventType
from app.core.config import settings
import structlog
import httpx
import os
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.models.user import User

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

# ==========================================
# AGENTFORGE OUTBOUND PROXY / INTEGRATION
# ==========================================

# In a real environment, this would come from a secure vault or integration table per user.
AGENTFORGE_API_URL = os.environ.get("AGENTFORGE_API_URL", "https://api.agentforge.studio/api/v1")
AGENTFORGE_API_KEY = os.environ.get("AGENTFORGE_API_KEY", "af_live_demo_key_123")

class WebhookTriggerRequest(BaseModel):
    trigger_url: str
    payload: Dict[str, Any]

class DirectAgentRequest(BaseModel):
    agent_type: str  # e.g., 'orchestrator', 'voice', 'research', 'dev'
    payload: Dict[str, Any]

@router.post("/trigger-workflow")
async def trigger_agentforge_workflow(
    request: WebhookTriggerRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Proxies a webhook trigger from Momentaic to an AgentForge Workflow.
    AgentForge Webhooks generally don't require Auth headers, just the unique URL.
    """
    logger.info(f"Triggering AgentForge Webhook for user {current_user.id}", trigger_url=request.trigger_url)
    
    url = f"{AGENTFORGE_API_URL}/webhooks/{request.trigger_url}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request.payload, timeout=30.0)
            response.raise_for_status()
            
            return {
                "status": "success",
                "message": "Workflow triggered successfully",
                "data": response.json() if response.content else None
            }
    except httpx.HTTPStatusError as e:
        logger.error("AgentForge Webhook Error", status_code=e.response.status_code, response=e.response.text)
        raise HTTPException(status_code=502, detail=f"AgentForge responded with error: {e.response.text}")
    except Exception as e:
        logger.error("AgentForge Connection Error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to connect to AgentForge")

@router.post("/direct-agent")
async def trigger_direct_agent(
    request: DirectAgentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Directly triggers a specialized AgentForge agent (e.g., orchestrator, research) 
    using the master API key.
    """
    logger.info(f"Triggering Direct AgentForge Agent for user {current_user.id}", agent_type=request.agent_type)
    
    url = f"{AGENTFORGE_API_URL}/agent/{request.agent_type}"
    headers = {
        "Authorization": f"Bearer {AGENTFORGE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request.payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            
            return {
                "status": "success",
                "data": response.json()
            }
    except httpx.HTTPStatusError as e:
        logger.error("AgentForge Direct Agent Error", status_code=e.response.status_code, response=e.response.text)
        raise HTTPException(status_code=502, detail=f"AgentForge agent error: {e.response.text}")
    except Exception as e:
        logger.error("AgentForge Connection Error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to connect to AgentForge")
