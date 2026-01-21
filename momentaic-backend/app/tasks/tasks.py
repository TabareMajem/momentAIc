"""
Celery Tasks
Background tasks for workflows, signals, content, and more
"""

from celery import shared_task
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
import structlog
import asyncio

logger = structlog.get_logger()


# Helper to run async code in Celery
def run_async(coro):
    """Run async coroutine in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ==================
# Workflow Tasks
# ==================

@shared_task(name="app.tasks.workflow.execute_workflow")
def execute_workflow(run_id: str, workflow_id: str) -> Dict[str, Any]:
    """
    Execute a workflow asynchronously.
    """
    logger.info("Executing workflow", run_id=run_id, workflow_id=workflow_id)
    
    async def _execute():
        from app.core.database import async_session_maker
        from sqlalchemy import select
        from app.models.workflow import Workflow, WorkflowRun, WorkflowRunStatus, WorkflowLog, LogLevel
        
        async with async_session_maker() as db:
            # Get workflow and run
            run_result = await db.execute(
                select(WorkflowRun).where(WorkflowRun.id == UUID(run_id))
            )
            run = run_result.scalar_one_or_none()
            
            if not run:
                logger.error("Run not found", run_id=run_id)
                return {"error": "Run not found"}
            
            wf_result = await db.execute(
                select(Workflow).where(Workflow.id == UUID(workflow_id))
            )
            workflow = wf_result.scalar_one_or_none()
            
            if not workflow:
                logger.error("Workflow not found", workflow_id=workflow_id)
                run.status = WorkflowRunStatus.FAILED
                run.error_message = "Workflow not found"
                await db.commit()
                return {"error": "Workflow not found"}
            
            try:
                run.status = WorkflowRunStatus.RUNNING
                run.started_at = datetime.utcnow()
                await db.commit()
                
                # Execute nodes
                context = dict(run.inputs or {})
                
                for node in workflow.nodes:
                    node_id = node.get("id")
                    node_type = node.get("type")
                    node_label = node.get("label", node_id)
                    
                    # Log start
                    log = WorkflowLog(
                        run_id=run.id,
                        node_id=node_id,
                        level=LogLevel.INFO,
                        message=f"Starting node: {node_label}",
                    )
                    db.add(log)
                    
                    run.current_node_id = node_id
                    await db.commit()
                    
                    # Execute based on type
                    result = await execute_node(node, context)
                    context[f"{node_id}_output"] = result
                    
                    # Log completion
                    log = WorkflowLog(
                        run_id=run.id,
                        node_id=node_id,
                        level=LogLevel.SUCCESS,
                        message=f"Completed node: {node_label}",
                        metadata={"output": str(result)[:500]},
                    )
                    db.add(log)
                    await db.commit()
                
                # Complete
                run.status = WorkflowRunStatus.COMPLETED
                run.completed_at = datetime.utcnow()
                run.outputs = context
                workflow.success_count += 1
                
                await db.commit()
                
                logger.info("Workflow completed", run_id=run_id)
                return {"status": "completed", "outputs": context}
                
            except Exception as e:
                logger.error("Workflow execution error", run_id=run_id, error=str(e))
                
                run.status = WorkflowRunStatus.FAILED
                run.error_message = str(e)
                run.error_node_id = run.current_node_id
                run.completed_at = datetime.utcnow()
                
                await db.commit()
                return {"status": "failed", "error": str(e)}
    
    return run_async(_execute())


async def execute_node(node: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """Execute a single workflow node"""
    from app.models.workflow import NodeType
    
    node_type = node.get("type")
    config = node.get("config", {})
    
    if node_type == NodeType.AI.value:
        return await execute_ai_node(config, context)
    elif node_type == NodeType.HTTP.value:
        return await execute_http_node(config, context)
    elif node_type == NodeType.CODE.value:
        return await execute_code_node(config, context)
    elif node_type == NodeType.TRANSFORM.value:
        return await execute_transform_node(config, context)
    elif node_type == NodeType.NOTIFICATION.value:
        return await execute_notification_node(config, context)
    else:
        return {"executed": True, "type": node_type}


async def execute_ai_node(config: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """Execute AI node"""
    from app.agents.base import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    llm = get_llm(config.get("model", "gemini-pro"))
    
    if not llm:
        return {"result": "AI not configured", "mock": True}
    
    prompt = config.get("prompt_template", "Process: {input}")
    for key, value in context.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return {"result": response.content}


async def execute_http_node(config: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """Execute HTTP request node"""
    import httpx
    
    url = config.get("url", "")
    method = config.get("method", "GET")
    
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, timeout=30)
        return {"status": response.status_code, "data": response.text[:1000]}


async def execute_code_node(config: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """Execute code node (sandboxed)"""
    # In production, use a sandboxed execution environment
    code = config.get("code", "result = 'Hello'")
    return {"executed": True, "code_length": len(code)}


async def execute_transform_node(config: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """Execute data transformation node"""
    transform_type = config.get("transform", "passthrough")
    input_key = config.get("input_key", "input")
    
    data = context.get(input_key, "")
    
    if transform_type == "uppercase":
        return str(data).upper()
    elif transform_type == "lowercase":
        return str(data).lower()
    elif transform_type == "json_parse":
        import json
        return json.loads(str(data))
    else:
        return data


async def execute_notification_node(config: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """Execute notification node"""
    channel = config.get("channel", "email")
    message = config.get("message", "Workflow completed")
    
    # In production, actually send notification
    return {"notified": True, "channel": channel, "message": message}


# ==================
# Signal Tasks
# ==================

@shared_task(name="app.tasks.signals.calculate_all_signals")
def calculate_all_signals() -> Dict[str, Any]:
    """
    Calculate signals for all active startups.
    Runs daily via Celery Beat.
    """
    logger.info("Starting daily signal calculation")
    
    async def _calculate():
        from app.core.database import async_session_maker
        from sqlalchemy import select
        from app.models.startup import Startup
        from app.api.v1.endpoints.signals import calculate_signals
        
        async with async_session_maker() as db:
            result = await db.execute(select(Startup))
            startups = result.scalars().all()
            
            calculated = 0
            errors = 0
            
            for startup in startups:
                try:
                    await calculate_signals(startup, db)
                    calculated += 1
                except Exception as e:
                    logger.error(
                        "Signal calculation error",
                        startup_id=str(startup.id),
                        error=str(e)
                    )
                    errors += 1
            
            await db.commit()
            
            return {"calculated": calculated, "errors": errors}
    
    return run_async(_calculate())


# ==================
# Content Tasks
# ==================

@shared_task(name="app.tasks.content.publish_scheduled_content")
def publish_scheduled_content() -> Dict[str, Any]:
    """
    Publish content that is scheduled for now or past.
    """
    logger.info("Checking scheduled content")
    
    async def _publish():
        from app.core.database import async_session_maker
        from sqlalchemy import select
        from app.models.growth import ContentItem, ContentStatus
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(ContentItem).where(
                    ContentItem.status == ContentStatus.SCHEDULED,
                    ContentItem.scheduled_for <= datetime.utcnow()
                )
            )
            items = result.scalars().all()
            
            published = 0
            
            for item in items:
                try:
                    # In production, actually publish to platform
                    item.status = ContentStatus.PUBLISHED
                    item.published_at = datetime.utcnow()
                    published += 1
                    
                    logger.info(
                        "Content published",
                        content_id=str(item.id),
                        platform=item.platform.value
                    )
                except Exception as e:
                    logger.error(
                        "Content publish error",
                        content_id=str(item.id),
                        error=str(e)
                    )
            
            await db.commit()
            
            return {"published": published}
    
    return run_async(_publish())


# ==================
# Growth Tasks
# ==================

@shared_task(name="app.tasks.growth.process_autopilot_leads")
def process_autopilot_leads() -> Dict[str, Any]:
    """
    Process leads with autopilot enabled.
    """
    logger.info("Processing autopilot leads")
    
    async def _process():
        from app.core.database import async_session_maker
        from sqlalchemy import select
        from app.models.growth import Lead
        from app.models.startup import Startup
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(Lead).where(Lead.autopilot_enabled == True)
            )
            leads = result.scalars().all()
            
            processed = 0
            
            for lead in leads:
                # Check if follow-up is due
                agent_state = lead.agent_state or {}
                last_contact = lead.last_contacted_at
                interval_days = agent_state.get("followup_interval_days", 3)
                
                if last_contact and (datetime.utcnow() - last_contact).days < interval_days:
                    continue
                
                # Get startup context
                startup_result = await db.execute(
                    select(Startup).where(Startup.id == lead.startup_id)
                )
                startup = startup_result.scalar_one_or_none()
                
                if startup:
                    # Queue sales agent task
                    from app.agents.sales_agent import sales_agent
                    
                    try:
                        await sales_agent.run(
                            lead=lead,
                            startup_context={
                                "name": startup.name,
                                "description": startup.description,
                                "tagline": startup.tagline,
                            },
                            user_id=str(startup.owner_id),
                        )
                        processed += 1
                    except Exception as e:
                        logger.error(
                            "Autopilot lead error",
                            lead_id=str(lead.id),
                            error=str(e)
                        )
            
            return {"processed": processed}
    
    return run_async(_process())


# ==================
# Auth Tasks
# ==================

@shared_task(name="app.tasks.auth.cleanup_expired_tokens")
def cleanup_expired_tokens() -> Dict[str, Any]:
    """
    Clean up expired refresh tokens.
    """
    logger.info("Cleaning up expired tokens")
    
    async def _cleanup():
        from app.core.database import async_session_maker
        from sqlalchemy import delete
        from app.models.user import RefreshToken
        
        async with async_session_maker() as db:
            result = await db.execute(
                delete(RefreshToken).where(
                    RefreshToken.expires_at < datetime.utcnow()
                )
            )
            await db.commit()
            
            return {"deleted": result.rowcount}
    
    return run_async(_cleanup())


# ==================
# Email Tasks
# ==================

@shared_task(name="app.tasks.email.send_email")
def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: str = None,
) -> Dict[str, Any]:
    """
    Send an email via SMTP.
    """
    logger.info("Sending email", to=to_email, subject=subject)
    
    from app.core.config import settings
    
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured, email not sent")
        return {"sent": False, "reason": "SMTP not configured"}
    
    # [PHASE 25 FIX] Real SMTP implementation
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        msg["To"] = to_email
        
        # HTML body
        html_part = MIMEText(body, "html")
        msg.attach(html_part)
        
        # Connect and send
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())
        
        logger.info("Email sent successfully", to=to_email)
        return {"sent": True, "to": to_email, "subject": subject}
        
    except Exception as e:
        logger.error("Email send failed", error=str(e), to=to_email)
        return {"sent": False, "reason": str(e)}

