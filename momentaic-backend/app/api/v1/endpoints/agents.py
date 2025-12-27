"""
Agent Swarm Endpoints
Multi-agent chat system with supervisor routing
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json
import asyncio

from app.core.database import get_db
from app.core.security import get_current_active_user, verify_startup_access, require_credits
from app.core.config import settings
from app.models.user import User
from app.models.startup import Startup
from app.models.conversation import Conversation, Message, AgentType, MessageRole
from app.schemas.agent import (
    ConversationCreate, ConversationResponse, ConversationWithMessages,
    ConversationListResponse, MessageCreate, MessageResponse,
    AgentChatRequest, AgentChatResponse, AgentInfoResponse, AvailableAgentsResponse,
    VisionPortalRequest, VisionPortalResponse, VisionPortalStatusResponse,
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
        "name": startup.name,
        "description": startup.description,
        "tagline": startup.tagline,
        "industry": startup.industry,
        "stage": startup.stage.value,
        "metrics": startup.metrics,
    } if chat_request.include_context else {}
    
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
            agent_type=routed_to,
            message=chat_request.message,
            startup_context=startup_context,
            user_id=str(current_user.id),
        )
        response_text = agent_response.get("response", response_text)
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=response_text,
        agent_type=routed_to or conversation.agent_type,
        metadata={"routed_to": routed_to.value if routed_to else None},
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
) -> dict:
    """
    Get response from a specialized agent.
    Routes to the appropriate agent instance based on type.
    """
    from app.agents import (
        sales_agent, content_agent, tech_lead_agent,
        finance_cfo_agent, legal_counsel_agent, growth_hacker_agent,
        product_pm_agent,
    )
    
    # Map agent types to instances
    agent_map = {
        AgentType.SALES_HUNTER: sales_agent,
        AgentType.CONTENT_CREATOR: content_agent,
        AgentType.TECH_LEAD: tech_lead_agent,
        AgentType.FINANCE_CFO: finance_cfo_agent,
        AgentType.LEGAL_COUNSEL: legal_counsel_agent,
        AgentType.GROWTH_HACKER: growth_hacker_agent,
        AgentType.PRODUCT_PM: product_pm_agent,
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
    current_user: User = Depends(require_credits(settings.credit_cost_agent_chat, "Agent chat")),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a chat response.
    
    Returns server-sent events with response chunks.
    """
    await verify_startup_access(chat_request.startup_id, current_user, db)
    
    async def generate():
        # Simplified streaming - in production, use actual LLM streaming
        response = "I'm analyzing your question and preparing a response..."
        
        for chunk in response.split():
            yield f"data: {json.dumps({'chunk': chunk + ' ', 'is_final': False})}\n\n"
            await asyncio.sleep(0.05)
        
        yield f"data: {json.dumps({'chunk': '', 'is_final': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


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
                except:
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
            except:
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
