"""
Persona Agents
Specialized agents with strong personalities (Elon, Paul, etc.)
"""
from typing import Dict, Any, List
import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base import get_llm, build_system_prompt
from app.models.conversation import AgentType

logger = structlog.get_logger()

class PersonaAgent:
    """
    Generic handler for Persona-based agents.
    Everything is driven by the system prompt in base.py AGENT_CONFIGS.
    """
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        # Personas need high creativity, so we use slightly higher temperature
        self.llm = get_llm("gemini-2.0-flash", temperature=0.8)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        history: List[Dict[str, str]] = []
    ) -> Dict[str, Any]:
        """Process a message with the specific persona"""
        
        if not self.llm:
            return {
                "response": "AI Service Unavailable (Check API Keys)",
                "agent": self.agent_type,
                "error": True
            }
            
        try:
            # 1. Build Deep Context System Prompt
            system_prompt = build_system_prompt(self.agent_type, startup_context)
            
            # 2. Construct Message History
            messages = [SystemMessage(content=system_prompt)]
            
            # Add recent history (last 5 messages) for continuity
            for msg in history[-5:]:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                else:
                    messages.append(AIMessage(content=msg['content']))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # 3. Invoke LLM
            response = await self.llm.ainvoke(messages)
            
            return {
                "response": response.content,
                "agent": self.agent_type,
                "tools_used": []
            }
            
        except Exception as e:
            logger.error(f"{self.agent_type} agent error", error=str(e))
            return {
                "response": f"Error: {str(e)}", 
                "agent": self.agent_type, 
                "error": True
            }

# Instances
elon_agent = PersonaAgent(AgentType.ELON_MUSK)
paul_agent = PersonaAgent(AgentType.PAUL_GRAHAM)
