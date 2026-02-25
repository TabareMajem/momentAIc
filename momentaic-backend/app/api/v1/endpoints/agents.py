"""
Agent Swarm Endpoints
Multi-agent chat system with supervisor routing
"""

from typing import Any, List, Optional
import structlog
import uuid
import json
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
import asyncio

from app.core.database import get_db
from app.core.security import (
    get_current_active_user, verify_startup_access, require_credits
)
from app.core.config import settings
from app.models.user import User
from app.models.startup import Startup
from app.models.conversation import Conversation, Message, AgentType, MessageRole
from app.schemas.agent import (
    ConversationCreate, ConversationResponse, ConversationWithMessages,
    ConversationListResponse, MessageCreate, MessageResponse,
    AgentChatRequest, AgentChatResponse, AgentInfoResponse, AvailableAgentsResponse,
    VisionPortalRequest, VisionPortalResponse, VisionPortalStatusResponse,
    BuilderChatRequest, GenerateImageRequest, ImageGenerationResponse,
    GenerateVideoRequest, VideoGenerationResponse,
    AgentFeedbackRequest,
)

router = APIRouter()


# ==================
# Conversations
# ==================

@router.get("/conversations", response_model=List[ConversationListResponse])
async def list_conversations(
    startup_id: UUID,
    limit: int = Query(20, le=50),
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List conversations for a startup.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.startup_id == startup_id,
            Conversation.user_id == current_user.id
        )
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    conversations = result.scalars().all()
    
    response = []
    for conv in conversations:
        # Get last message preview
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        
        response.append(ConversationListResponse(
            id=conv.id,
            title=conv.title,
            agent_type=conv.agent_type,
            message_count=conv.message_count,
            last_message_preview=last_msg.content[:100] if last_msg else None,
            updated_at=conv.updated_at,
        ))
    
    return response


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    startup_id: UUID,
    conv_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new conversation.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    conversation = Conversation(
        startup_id=startup_id,
        user_id=current_user.id,
        agent_type=conv_data.agent_type,
        title=conv_data.title,
        context=conv_data.initial_context or {},
    )
    
    db.add(conversation)
    await db.flush()
    
    return ConversationResponse.model_validate(conversation)


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    startup_id: UUID,
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a conversation with its messages.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.startup_id == startup_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationWithMessages.model_validate(conversation)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    startup_id: UUID,
    conversation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a conversation.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.startup_id == startup_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)


# ==================
# Chat
# ==================

@router.post("/chat", response_model=AgentChatResponse)
async def chat(
    chat_request: AgentChatRequest,
    request: Request,
    current_user: User = Depends(require_credits(settings.credit_cost_agent_chat, "Agent chat")),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to an agent and get a response.
    
    The supervisor agent routes to the appropriate specialist.
    Costs 1 credit per message.
    """
    await verify_startup_access(chat_request.startup_id, current_user, db)
    
    # Get or create conversation
    conversation_id = chat_request.conversation_id
    
    if conversation_id:
        conv_result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.startup_id == chat_request.startup_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Create new conversation
        conversation = Conversation(
            startup_id=chat_request.startup_id,
            user_id=current_user.id,
            agent_type=chat_request.agent_type,
            title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
        )
        db.add(conversation)
        await db.flush()
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=chat_request.message,
    )
    db.add(user_message)
    conversation.message_count += 1
    
    # Get startup context
    startup_result = await db.execute(
        select(Startup).where(Startup.id == chat_request.startup_id)
    )
    startup = startup_result.scalar_one()
    
    startup_context = {
        "startup_id": str(chat_request.startup_id),
        "name": startup.name,
        "description": startup.description,
        "tagline": startup.tagline,
        "industry": startup.industry,
        "stage": startup.stage.value,
        "metrics": startup.metrics,
        "locale": request.headers.get("accept-language", "en"),
    } if chat_request.include_context else {
        "startup_id": str(chat_request.startup_id),
        "locale": request.headers.get("accept-language", "en")
    }

    # Inject Agent Memory Context
    from app.services.agent_memory_service import agent_memory_service
    memory_context = await agent_memory_service.recall_as_context(
        startup_id=str(chat_request.startup_id),
        agent_name=chat_request.agent_type.value,
        limit=5
    )
    if memory_context:
        startup_context["agent_memory"] = memory_context
        
    # Inject Cross-Startup Intelligence
    if chat_request.include_context and startup.industry:
        from app.services.cross_startup_intelligence import cross_startup_intelligence
        hive_mind_context = await cross_startup_intelligence.format_insights_for_prompt(
            db=db, industry=startup.industry
        )
        if hive_mind_context:
            startup_context["agent_memory"] = startup_context.get("agent_memory", "") + "\n\n" + hive_mind_context
    
    # Route through supervisor
    from app.agents.supervisor import supervisor_agent
    
    routing_result = await supervisor_agent.route(
        message=chat_request.message,
        startup_context=startup_context,
        user_id=str(current_user.id),
        startup_id=str(chat_request.startup_id),
    )
    
    routed_to = None
    response_text = routing_result.get("response", "I'm sorry, I couldn't process that request.")
    
    if routing_result.get("routed") and routing_result.get("route_to"):
        routed_to = AgentType(routing_result["route_to"])
        
        # Get response from specialized agent
        agent_response = await _get_agent_response(
            agent_type=routed_to or conversation.agent_type,
            message=chat_request.message,
            startup_context=startup_context,
            user_id=str(current_user.id),
            db=db,
        )
        response_text = agent_response.get("response", response_text)
    
    # [KILL SHOT 2] Ensure Agent Replay data persists 
    msg_meta = {"routed_to": routed_to.value if routed_to else None}
    if agent_response and "chain_of_thought" in agent_response:
        msg_meta["chain_of_thought"] = agent_response["chain_of_thought"]
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=response_text,
        agent_type=routed_to or conversation.agent_type,
        message_meta=msg_meta,
    )
    db.add(assistant_message)
    conversation.message_count += 1
    
    await db.flush()
    
    return AgentChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        response=response_text,
        agent_type=assistant_message.agent_type or AgentType.SUPERVISOR,
        routed_to=routed_to,
        tool_calls=[],
        credits_used=1,
        metadata={},
    )


async def _get_agent_response(
    agent_type: AgentType,
    message: str,
    startup_context: dict,
    user_id: str,
    db: AsyncSession = None,
) -> dict:
    """
    Get response from a specialized agent.
    Routes to the appropriate agent instance based on type.
    """
    from app.services.live_data_service import live_data_service
    from app.agents import (
        sales_agent, content_agent, tech_lead_agent,
        finance_cfo_agent, legal_counsel_agent, growth_hacker_agent,
        product_pm_agent, planning_agent,
    )
    
    # 💰 [KILL SHOT 1] Inject Real-time Revenue Data
    if db and startup_context and startup_context.get("startup_id"):
        try:
            live_revenue = await live_data_service.get_live_revenue(startup_context["startup_id"], db)
            if live_revenue:
                # Merge into metrics block
                if "metrics" not in startup_context:
                    startup_context["metrics"] = {}
                startup_context["metrics"]["mrr"] = live_revenue["monthly_recurring_revenue"]
                startup_context["metrics"]["churn"] = live_revenue["churn_rate_percent"]
                startup_context["metrics"]["live_revenue_data"] = live_revenue
        except Exception as e:
            import structlog
            logger = structlog.get_logger()
            logger.error("Failed to inject live revenue", error=str(e))
    
    # Map agent types to instances
    agent_map = {
        AgentType.SALES_HUNTER: sales_agent,
        AgentType.CONTENT_CREATOR: content_agent,
        AgentType.TECH_LEAD: tech_lead_agent,
        AgentType.FINANCE_CFO: finance_cfo_agent,
        AgentType.LEGAL_COUNSEL: legal_counsel_agent,
        AgentType.GROWTH_HACKER: growth_hacker_agent,
        AgentType.PRODUCT_PM: product_pm_agent,
        AgentType.PLANNING_AGENT: planning_agent,
    }
    
    agent = agent_map.get(agent_type)
    
    if agent:
        try:
            result = await agent.process(
                message=message,
                startup_context=startup_context,
                user_id=user_id,
            )
            return result
        except Exception as e:
            import structlog
            logger = structlog.get_logger()
            logger.error("Agent response error", agent=agent_type.value, error=str(e))
    
    # Fallback to generic LLM response
    from app.agents.base import get_llm, get_agent_config
    from langchain_core.messages import HumanMessage, SystemMessage
    
    config = get_agent_config(agent_type)
    llm = get_llm("gemini-pro")
    
    if not llm:
        return {"response": f"[{config['name']}] I'd be happy to help with that. How can I assist you further?"}
    
    context_section = ""
    if startup_context:
        context_section = f"""
Startup Context:
- Name: {startup_context.get('name')}
- Industry: {startup_context.get('industry')}
- Stage: {startup_context.get('stage')}
- Description: {startup_context.get('description', '')}

{startup_context.get('agent_memory', '')}
"""
    
    prompt = f"""{context_section}

User Question: {message}

Provide a helpful, actionable response."""
    
    try:
        response = await llm.ainvoke([
            SystemMessage(content=config["system_prompt"]),
            HumanMessage(content=prompt),
        ])
        return {"response": response.content}
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Agent response error", agent=agent_type.value, error=str(e))
        return {"response": f"I apologize, but I encountered an error. Please try again."}


@router.post("/chat/stream")
async def chat_stream(
    chat_request: AgentChatRequest,
    request: Request,
    current_user: User = Depends(require_credits(settings.credit_cost_agent_chat, "Agent chat")),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a chat response.
    
    Returns server-sent events with response chunks.
    Event format: data: {"chunk": "token", "is_final": false, "metadata": {...}}
    """
    await verify_startup_access(chat_request.startup_id, current_user, db)
    
    # Get startup context (reuse logic from chat endpoint)
    conversation_id = chat_request.conversation_id
    if not conversation_id:
        # Create new conversation logic would go here, for now require conversation_id or create basic
        pass 

    startup_result = await db.execute(select(Startup).where(Startup.id == chat_request.startup_id))
    startup = startup_result.scalar_one()
    
    startup_context = {
        "startup_id": str(chat_request.startup_id),
        "name": startup.name,
        "description": startup.description,
        "industry": startup.industry,
        "stage": startup.stage.value,
        "metrics": startup.metrics,
        "locale": request.headers.get("accept-language", "en"),
    } if chat_request.include_context else {
        "startup_id": str(chat_request.startup_id),
        "locale": request.headers.get("accept-language", "en")
    }

    # Inject Agent Memory Context
    from app.services.agent_memory_service import agent_memory_service
    memory_context = await agent_memory_service.recall_as_context(
        startup_id=str(chat_request.startup_id),
        agent_name=chat_request.agent_type.value,
        limit=5
    )
    if memory_context:
        startup_context["agent_memory"] = memory_context
        
    # Inject Cross-Startup Intelligence
    if chat_request.include_context and startup.industry:
        from app.services.cross_startup_intelligence import cross_startup_intelligence
        hive_mind_context = await cross_startup_intelligence.format_insights_for_prompt(
            db=db, industry=startup.industry
        )
        if hive_mind_context:
            startup_context["agent_memory"] = startup_context.get("agent_memory", "") + "\n\n" + hive_mind_context

    async def event_generator():
        # 1. Supervisor Routing (Synchronous Step)
        from app.agents.supervisor import supervisor_agent
        
        yield f"data: {json.dumps({'chunk': '', 'is_final': False, 'status': 'Routing...'})}\n\n"
        
        routing_result = await supervisor_agent.route(
            message=chat_request.message,
            startup_context=startup_context,
            user_id=str(current_user.id),
            startup_id=str(chat_request.startup_id),
        )
        
        routed_to = None
        if routing_result.get("routed") and routing_result.get("route_to"):
            routed_to = AgentType(routing_result["route_to"])
            yield f"data: {json.dumps({'chunk': '', 'is_final': False, 'status': f'Routed to {routed_to.value}'})}\n\n"
            
            from app.core.websocket import websocket_manager
            import asyncio
            from datetime import datetime
            
            asyncio.create_task(websocket_manager.broadcast_to_startup(
                str(chat_request.startup_id),
                {
                    "type": "agent_action",
                    "agent": "supervisor",
                    "action": f"Delegating task to {routed_to.value}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ))
        
        # 2. Agent Processing (Streaming)
        if routed_to:
            # specialized agent streaming
            from app.agents import (
                growth_hacker_agent, sales_agent, content_agent, 
                tech_lead_agent, finance_cfo_agent, legal_counsel_agent, product_pm_agent, planning_agent
            )
            agent_map = {
                AgentType.GROWTH_HACKER: growth_hacker_agent,
                AgentType.SALES_HUNTER: sales_agent,
                AgentType.CONTENT_CREATOR: content_agent,
                AgentType.TECH_LEAD: tech_lead_agent,
                AgentType.FINANCE_CFO: finance_cfo_agent,
                AgentType.LEGAL_COUNSEL: legal_counsel_agent,
                AgentType.PRODUCT_PM: product_pm_agent,
                AgentType.PLANNING_AGENT: planning_agent,
            }
            agent = agent_map.get(routed_to)
            
            if agent and hasattr(agent, "stream_process"):
                async for chunk in agent.stream_process(chat_request.message, startup_context, str(current_user.id)):
                    yield f"data: {json.dumps({'chunk': chunk, 'is_final': False})}\n\n"
            else:
                # Fallback to non-streaming if method missing
                result = await _get_agent_response(routed_to, chat_request.message, startup_context, str(current_user.id), db=db)
                yield f"data: {json.dumps({'chunk': result.get('response', ''), 'is_final': False})}\n\n"
        else:
            # 3. Generic LLM Fallback (Streaming)
            from app.agents.base import get_llm, get_agent_config
            from langchain_core.messages import HumanMessage, SystemMessage
            
            llm = get_llm("gemini-2.0-flash") # Use fast model
            if llm:
                config = get_agent_config(AgentType.SUPERVISOR)
                prompt = f"""Startup Context: {json.dumps({k:v for k,v in startup_context.items() if k != 'agent_memory'})}\n{startup_context.get('agent_memory', '')}\nUser Question: {chat_request.message}"""
                
                async for chunk in llm.astream([
                    SystemMessage(content=config["system_prompt"]),
                    HumanMessage(content=prompt)
                ]):
                    if chunk.content:
                        yield f"data: {json.dumps({'chunk': chunk.content, 'is_final': False})}\n\n"
            else:
                 yield f"data: {json.dumps({'chunk': routing_result.get('response', 'Error'), 'is_final': False})}\n\n"

        yield f"data: {json.dumps({'chunk': '', 'is_final': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ==================
# Agent Info
# ==================

@router.get("/available", response_model=AvailableAgentsResponse)
async def get_available_agents():
    """
    Get list of available agents and their capabilities.
    """
    from app.agents.base import AGENT_CONFIGS
    
    agents = []
    for agent_type, config in AGENT_CONFIGS.items():
        if agent_type == AgentType.SUPERVISOR:
            continue
        
        agents.append(AgentInfoResponse(
            type=agent_type,
            name=config["name"],
            description=config["description"],
            capabilities=config.get("system_prompt", "").split("\n")[:5],
            available_tools=[t.name for t in config.get("tools", [])],
        ))
    
    return AvailableAgentsResponse(agents=agents)

# ==================
# Agent Feedback
# ==================

@router.post("/feedback")
async def submit_agent_feedback(
    request: AgentFeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit user feedback for an agent output to fuel the Feedback Learning System.
    Stores the feedback in the agent's persistent memory.
    """
    await verify_startup_access(request.startup_id, current_user, db)
    
    from app.services.agent_memory_service import AgentMemoryService
    
    memory_service = AgentMemoryService()
    
    # Store explicit text feedback as a preference
    if request.feedback_text:
        await memory_service.remember(
            startup_id=str(request.startup_id),
            agent_name=request.agent_type.value,
            key=f"user_preference_{uuid.uuid4().hex[:8]}",
            value=f"{'POSITIVE' if request.is_positive else 'NEGATIVE'} FEEDBACK: {request.feedback_text}",
            memory_type="preference",
            importance=8 if not request.is_positive else 6, # Negative feedback is more important to correct
            metadata={
                "message_id": str(request.message_id) if request.message_id else None,
                "is_positive": request.is_positive
            }
        )
    
    return {"status": "success", "message": "Feedback recorded."}


# ==================
# Vision Portal (Code Generation)
# ==================

@router.post("/vision/generate", response_model=VisionPortalResponse)
async def generate_vision_portal(
    startup_id: UUID,
    vision_request: VisionPortalRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_vision_portal, "Vision Portal generation")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate code for an application using Vision Portal.
    
    Multi-step agent chain:
    1. PM Agent → User Stories
    2. Architect Agent → Database Schema
    3. Coder Agent → Code Generation
    
    Costs 20 credits.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    from app.agents.base import get_llm
    from langchain_core.messages import HumanMessage, SystemMessage
    
    llm = get_llm("gemini-pro")
    
    result = {
        "project_name": vision_request.app_description.split()[0].lower() + "_app",
        "user_stories": None,
        "database_schema": None,
        "api_specification": None,
        "generated_files": [],
        "architecture_diagram": None,
        "next_steps": [],
        "credits_used": settings.credit_cost_vision_portal,
    }
    
    if not llm:
        # Mock response
        result["generated_files"] = [
            {"path": "README.md", "content": f"# {result['project_name']}\n\n{vision_request.app_description}"},
            {"path": "package.json", "content": '{"name": "app", "version": "1.0.0"}'},
        ]
        result["next_steps"] = ["Set up development environment", "Install dependencies", "Start building!"]
        return VisionPortalResponse(**result)
    
    try:
        # Step 1: Product Manager - User Stories
        if vision_request.include_user_stories:
            pm_prompt = f"""As a Product Manager, create user stories for this app:

{vision_request.app_description}

Format as JSON array:
[
    {{"id": "US-001", "as_a": "user type", "i_want": "action", "so_that": "benefit", "acceptance_criteria": ["criteria1", "criteria2"]}}
]

Generate 5-10 user stories."""
            
            pm_response = await llm.ainvoke([
                SystemMessage(content="You are an expert Product Manager."),
                HumanMessage(content=pm_prompt),
            ])
            
            # Parse user stories
            import re
            json_match = re.search(r'\[[\s\S]*\]', pm_response.content)
            if json_match:
                try:
                    result["user_stories"] = json.loads(json_match.group())
                except Exception:
                    result["user_stories"] = [{"raw": pm_response.content}]
        
        # Step 2: Architect - Database Schema
        if vision_request.include_database_schema:
            arch_prompt = f"""As a Software Architect, design the database schema for:

{vision_request.app_description}

User Stories: {json.dumps(result.get('user_stories', [])[:3])}

Provide PostgreSQL schema with:
- Table definitions
- Relationships
- Indexes

Format as SQL CREATE statements."""
            
            arch_response = await llm.ainvoke([
                SystemMessage(content="You are an expert Software Architect."),
                HumanMessage(content=arch_prompt),
            ])
            
            result["database_schema"] = arch_response.content
            result["generated_files"].append({
                "path": "database/schema.sql",
                "content": arch_response.content,
            })
        
        # Step 3: API Spec
        if vision_request.include_api_spec:
            api_prompt = f"""Design REST API endpoints for:

{vision_request.app_description}

Format as OpenAPI-style JSON:
{{
    "endpoints": [
        {{"method": "GET", "path": "/users", "description": "...", "request": {{}}, "response": {{}}}}
    ]
}}"""
            
            api_response = await llm.ainvoke([
                SystemMessage(content="You are an API designer."),
                HumanMessage(content=api_prompt),
            ])
            
            try:
                json_match = re.search(r'\{[\s\S]*\}', api_response.content)
                if json_match:
                    result["api_specification"] = json.loads(json_match.group())
            except Exception:
                result["api_specification"] = {"raw": api_response.content}
        
        # Step 4: Generate Code Files
        code_prompt = f"""Generate starter code for a {vision_request.tech_stack} application:

{vision_request.app_description}

Generate these files:
1. Main entry point
2. Basic routing
3. Sample component/endpoint
4. Configuration file
5. README.md

For each file provide:
FILE: path/to/file.ext
```
code here
```"""
        
        code_response = await llm.ainvoke([
            SystemMessage(content=f"You are an expert {vision_request.tech_stack} developer."),
            HumanMessage(content=code_prompt),
        ])
        
        # Parse generated files
        file_pattern = re.compile(r'FILE:\s*(.+?)\n```\w*\n([\s\S]+?)```', re.MULTILINE)
        for match in file_pattern.finditer(code_response.content):
            result["generated_files"].append({
                "path": match.group(1).strip(),
                "content": match.group(2).strip(),
            })
        
        result["next_steps"] = [
            "Review generated user stories and refine requirements",
            "Set up database with provided schema",
            "Implement API endpoints",
            "Build frontend components",
            "Add authentication and authorization",
            "Write tests",
            "Deploy to staging",
        ]
        
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Vision Portal generation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )
    
    return VisionPortalResponse(**result)


# ==================
# Shared Brain (Memory Context)
# ==================

@router.get("/memory/shared-brain")
async def get_shared_brain(
    startup_id: UUID,
    limit: int = 10,
    min_importance: int = 7,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the agent's 'Shared Brain' context.
    Returns high-importance memories and current focus.
    """
    await verify_startup_access(startup_id, current_user, db)
    
    from app.models.conversation import AgentMemory
    
    # Fetch high importance memories
    result = await db.execute(
        select(AgentMemory)
        .where(
            AgentMemory.startup_id == startup_id,
            AgentMemory.importance >= min_importance
        )
        .order_by(AgentMemory.created_at.desc())
        .limit(limit)
    )
    memories = result.scalars().all()
    
    formatted_memories = [
        {
            "id": str(m.id),
            "type": m.memory_type,
            "content": m.content,
            "agent": m.agent_type.value,
            "importance": m.importance,
            "created_at": m.created_at.isoformat()
        } for m in memories
    ]
    
    return {
        "memories": formatted_memories,
        "count": len(formatted_memories),
        "status": "active"
    }


# ==================
# Judgement Agent (Optimization)
# ==================

class ContentOptimizationRequest(BaseModel):
    goal: str
    target_audience: str
    variations: List[str]

@router.post("/optimize/content")
async def optimize_content(
    request: ContentOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Use Judgement Agent to evaluate and pick the best content variation.
    """
    # Quick visual check simulation for UI demo (optional delay or event)
    from app.agents import judgement_agent
    
    result = await judgement_agent.evaluate_content(
        goal=request.goal,
        target_audience=request.target_audience,
        variations=request.variations
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result


@router.post("/marketing/optimize-loop")
async def optimize_loop(
    request: ContentOptimizationRequest, # Reusing same model for input
    topic: str = "", # Optional override
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the recursive feedback loop: Marketing -> Judge -> Marketing.
    """
    from app.agents import marketing_agent
    
    # Use topic from request if valid, or derive from goal
    search_topic = topic if topic else request.goal
    
    result = await marketing_agent.optimize_post_loop(
        topic=search_topic,
        goal=request.goal,
        target_audience=request.target_audience
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

# ==================
# Design & Image Generation
# ==================

@router.post("/design/generate-image", response_model=ImageGenerationResponse)
async def generate_image(
    request: GenerateImageRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_image_gen, "Image Generation")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an image using AI (Gemini Imagen 3).
    Deducts credits.
    """
    await verify_startup_access(request.startup_id, current_user, db)
    
    from app.agents.design_agent import design_agent
    
    image_url = await design_agent.generate_card_image(
        archetype_name=request.archetype,
        anime_style=request.style,
        description=request.prompt
    )
    
    return ImageGenerationResponse(
        image_url=image_url,
        credits_used=settings.credit_cost_image_gen
    )


@router.post("/design/generate-video", response_model=VideoGenerationResponse)
async def generate_video(
    request: GenerateVideoRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_video_gen, "Video Generation")),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a video using AI (PiAPI / Kling).
    Deducts credits (high cost).
    """
    await verify_startup_access(request.startup_id, current_user, db)
    
    from app.agents.design_agent import design_agent
    
    try:
        video_url = await design_agent.generate_video(
            prompt=request.prompt,
            model=request.model
        )
        
        return VideoGenerationResponse(
            video_url=video_url,
            credits_used=settings.credit_cost_video_gen
        )
    except Exception as e:
        # Refund credits if generation failed? 
        # For simplicity in this logical flow, we just raise error. 
        # In production, we'd handle transaction rollback or refund.
        raise HTTPException(status_code=500, detail=str(e))


# ==================
# Integration Builder
# ==================

class MonitorMarketRequest(BaseModel):
    startup_id: UUID
    known_competitors: List[str] = []

@router.post("/competitor/monitor")
async def monitor_market(
    request: MonitorMarketRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_competitor_monitor or 5, "Competitor Monitoring")),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the Competitor Intel Agent to scan the market.
    """
    await verify_startup_access(request.startup_id, current_user, db)
    
    # Get startup context
    startup_result = await db.execute(select(Startup).where(Startup.id == request.startup_id))
    startup = startup_result.scalar_one()
    
    context = {
        "name": startup.name,
        "description": startup.description,
        "industry": startup.industry,
    }
    
    from app.agents.competitor_intel_agent import competitor_intel_agent
    
    result = await competitor_intel_agent.monitor_market(
        startup_context=context,
        known_competitors=request.known_competitors
    )
    
    return result


class SalesHuntRequest(BaseModel):
    startup_id: UUID

@router.post("/sales/hunt")
async def hunt_leads(
    request: SalesHuntRequest,
    current_user: User = Depends(require_credits(settings.credit_cost_sales_hunt or 10, "Sales Lead Hunting")),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the Sales Hunter Agent to find and draft outreach for new leads.
    """
    await verify_startup_access(request.startup_id, current_user, db)
    
    startup_result = await db.execute(select(Startup).where(Startup.id == request.startup_id))
    startup = startup_result.scalar_one()
    
    context = {
        "name": startup.name,
        "description": startup.description,
        "industry": startup.industry,
        "tagline": startup.tagline
    }
    
    from app.agents.sales_agent import sales_agent
    
    result = await sales_agent.auto_hunt(
        startup_context=context,
        user_id=str(current_user.id)
    )
    
    # Auto-save found leads to DB
    if "leads" in result:
        leads_data = result["leads"] # List of dicts {lead, draft, verified}
        for item in leads_data:
            lead_info = item["lead"]
            # Create Lead in DB
            from app.models.growth import Lead, LeadStatus
            
            # Check dupes
            dupe_check = await db.execute(select(Lead).where(
                Lead.startup_id == request.startup_id, 
                Lead.company_website == lead_info.get("company_website")
            ))
            if dupe_check.scalar_one_or_none():
                continue

            new_lead = Lead(
                startup_id=request.startup_id,
                company_name=lead_info.get("company_name", "Unknown"),
                company_website=lead_info.get("company_website"),
                contact_name=lead_info.get("contact_name", "Unknown"),
                contact_title=lead_info.get("contact_title"),
                contact_email=lead_info.get("contact_email"),
                source="ai_hunter",
                status=LeadStatus.NEW,
                notes=f"Draft: {item.get('draft')}"
            )
            db.add(new_lead)
        await db.commit()
    
    return result
    message: str

@router.post("/builder/chat")
async def chat_builder(
    request: BuilderChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Direct line to the Integration Builder Agent.
    Generates real Python connector code.
    """
    from app.agents.integration_builder_agent import integration_builder_agent
    
    # 1. Process with Agent
    result = await integration_builder_agent.process(
        message=request.message,
        user_id=str(current_user.id)
    )
    
    # 2. Return result with file URL
    return {
        "response": result.get("response", "Code generated."),
        "file_url": result.get("file_url")
    }
