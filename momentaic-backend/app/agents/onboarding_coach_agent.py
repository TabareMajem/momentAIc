"""
Onboarding Coach Agent
Guides new users through the platform and helps them get started effectively
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, build_system_prompt
from app.models.conversation import AgentType

logger = structlog.get_logger()


# Define the startup journey phases
STARTUP_PHASES = {
    "idea": {
        "name": "Idea Stage",
        "description": "Validating your concept and finding product-market fit signals",
        "key_actions": [
            "Define your value proposition",
            "Identify target customer segments",
            "Validate the problem exists (talk to 10+ potential customers)",
            "Research competitors",
            "Draft a one-pager pitch"
        ],
        "recommended_agents": ["strategy", "paul_graham", "legal_counsel"],
        "next_phase": "build"
    },
    "build": {
        "name": "Build Stage",
        "description": "Creating your MVP and getting first users",
        "key_actions": [
            "Define MVP scope (ruthlessly cut features)",
            "Set up tech stack",
            "Build landing page",
            "Implement core feature loop",
            "Get 10 beta users"
        ],
        "recommended_agents": ["tech_lead", "product_pm", "design"],
        "next_phase": "launch"
    },
    "launch": {
        "name": "Launch Stage",
        "description": "Going to market and acquiring first paying customers",
        "key_actions": [
            "Finalize pricing strategy",
            "Prepare launch content (Product Hunt, social media)",
            "Set up analytics and tracking",
            "Execute launch campaign",
            "Get first 10 paying customers"
        ],
        "recommended_agents": ["launch_strategist", "marketing", "growth_hacker"],
        "next_phase": "grow"
    },
    "grow": {
        "name": "Growth Stage",
        "description": "Scaling acquisition and optimizing retention",
        "key_actions": [
            "Identify top acquisition channels",
            "Optimize conversion funnel",
            "Build referral/viral loops",
            "Reduce churn",
            "Reach $10K MRR"
        ],
        "recommended_agents": ["growth_hacker", "sales_hunter", "customer_success"],
        "next_phase": "scale"
    },
    "scale": {
        "name": "Scale Stage",
        "description": "Building the machine and preparing for fundraising",
        "key_actions": [
            "Build repeatable sales process",
            "Hire key team members",
            "Prepare fundraising materials",
            "Optimize unit economics",
            "Reach $100K+ MRR"
        ],
        "recommended_agents": ["finance_cfo", "hr_operations", "elon_musk"],
        "next_phase": None
    }
}


class OnboardingCoachAgent:
    """
    Onboarding Coach - Guides entrepreneurs through their startup journey
    
    Capabilities:
    - Assess current startup phase
    - Provide phase-specific guidance
    - Recommend next actions
    - Connect to relevant specialist agents
    - Track progress
    """
    
    def __init__(self):
        self.llm = get_llm("deepseek-chat", temperature=0.7)
    
    async def assess_phase(self, startup_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess which phase the startup is in based on context
        """
        stage = startup_context.get("stage", "idea")
        
        # Map database stage to our phases
        stage_mapping = {
            "idea": "idea",
            "mvp": "build",
            "growth": "grow",
            "scale": "scale"
        }
        
        current_phase = stage_mapping.get(stage, "idea")
        phase_info = STARTUP_PHASES.get(current_phase, STARTUP_PHASES["idea"])
        
        return {
            "current_phase": current_phase,
            "phase_name": phase_info["name"],
            "description": phase_info["description"],
            "key_actions": phase_info["key_actions"],
            "recommended_agents": phase_info["recommended_agents"],
            "next_phase": phase_info["next_phase"]
        }
    
    async def get_next_action(
        self,
        startup_context: Dict[str, Any],
        completed_actions: List[str] = []
    ) -> Dict[str, Any]:
        """
        Get the most important next action for the startup
        """
        phase_info = await self.assess_phase(startup_context)
        
        # Find uncompleted actions
        remaining_actions = [
            action for action in phase_info["key_actions"]
            if action not in completed_actions
        ]
        
        if not remaining_actions:
            # Phase complete, suggest moving to next
            next_phase = phase_info.get("next_phase")
            if next_phase:
                return {
                    "action_type": "phase_complete",
                    "message": f"🎉 Congratulations! You've completed the {phase_info['phase_name']}. Ready to move to {STARTUP_PHASES[next_phase]['name']}?",
                    "next_phase": next_phase
                }
            else:
                return {
                    "action_type": "journey_complete",
                    "message": "🚀 You've completed all phases! You're now in Scale mode. Keep iterating and growing!"
                }
        
        # Return the next priority action
        next_action = remaining_actions[0]
        
        # Find the best agent for this action
        recommended_agent = phase_info["recommended_agents"][0] if phase_info["recommended_agents"] else "general"
        
        return {
            "action_type": "next_action",
            "action": next_action,
            "phase": phase_info["phase_name"],
            "recommended_agent": recommended_agent,
            "remaining_count": len(remaining_actions),
            "message": f"Your next priority: **{next_action}**\n\nI recommend talking to the **{recommended_agent.replace('_', ' ').title()}** agent for help with this."
        }
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process a coaching request
        """
        if not self.llm:
            return {"response": "Coaching service unavailable", "agent": "onboarding_coach", "error": True}
        
        try:
            # Get phase context
            phase_info = await self.assess_phase(startup_context)
            
            # Build coaching prompt
            system_prompt = f"""You are the Advanced Onboarding AI for MomentAIc.
            
Your Goal: Deliver a "WOW" experience by providing deeply insightful, specific, and actionable advice.
You are NOT a generic chatbot. You are a Founding Architect.

Your Personality:
- Visionary yet pragmatic (Think Elon Musk x Paul Graham).
- Concise and punchy. Avoid fluff.
- Extremely focused on maximizing leverage and speed.
- You assume the user is smart and ambitious.

Current Startup Context:
- Name: {startup_context.get('name', 'Your Startup')}
- Industry: {startup_context.get('industry', 'Technology')}
- Phase: {phase_info['phase_name']} ({phase_info['description']})

Key Priorities:
{chr(10).join(f'- {action}' for action in phase_info['key_actions'])}

Recommended Specialists: {', '.join(phase_info['recommended_agents'])}

Instruction:
- Answer the user's question directly.
- If they ask what to do, bias towards the Key Priorities.
- Always end with a provocative question or a specific next step to keep momentum.
- Use markdown formatting for readability.
"""

            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ])
            
            return {
                "response": response.content,
                "agent": "onboarding_coach",
                "phase_info": phase_info,
                "tools_used": []
            }
            
        except Exception as e:
            logger.error("Onboarding coach error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "onboarding_coach", "error": True}
    
    async def generate_welcome_message(self, startup_context: Dict[str, Any]) -> str:
        """
        Generate a personalized welcome message for new users
        """
        phase_info = await self.assess_phase(startup_context)
        name = startup_context.get("name", "your startup")
        
        return f"""👋 Welcome to MomentAIc!

I'm your **Onboarding Coach**. I'll help guide {name} through the startup journey.

📍 **Current Phase**: {phase_info['phase_name']}
{phase_info['description']}

🎯 **Your Priority Actions**:
{chr(10).join(f'  • {action}' for action in phase_info['key_actions'][:3])}

💡 **Pro Tip**: Talk to the **{phase_info['recommended_agents'][0].replace('_', ' ').title()}** agent to get started on your first action.

Type "What should I focus on?" to get personalized guidance, or ask me anything about your startup journey!"""


# Singleton
onboarding_coach_agent = OnboardingCoachAgent()
