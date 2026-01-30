"""
LLM Context Service
Generates llms.txt and related metadata for agentic crawlers.
"""
from typing import Dict, Any, List
import structlog
from app.agents.base import AGENT_CONFIGS, AgentType

logger = structlog.get_logger()

class LLMContextService:
    """Service to generate LLM-readable documentation"""
    
    def generate_llms_txt(self) -> str:
        """
        Generate concise llms.txt
        Format:
        # Title
        > Description
        
        ## Agents
        - Name: Description
        """
        lines = [
            "# MomentAIc: The Entrepreneur Operating System",
            "> An AI-Native platform for building and scaling startups autonomously.",
            "",
            "## Core Agents",
            "The following agents are available to perform specialized tasks:",
            ""
        ]
        
        for agent_type, config in AGENT_CONFIGS.items():
            lines.append(f"- **{config['name']}**: {config['description']}")
            
        lines.append("")
        lines.append("## API Usage")
        lines.append("To interact with these agents, use the `/api/v1/conversation` endpoint.")
        lines.append("See /llms-full.txt for detailed schema and tool definitions.")
        
        return "\n".join(lines)

    def generate_llms_full_txt(self) -> str:
        """
        Generate detailed llms-full.txt including system prompts and tools
        """
        lines = [
            "# MomentAIc Full Documentation",
            "",
            "## Agent Registry",
            ""
        ]
        
        for agent_type, config in AGENT_CONFIGS.items():
            lines.append(f"### {config['name']}")
            lines.append(f"**Type**: `{agent_type.value}`")
            lines.append(f"**Description**: {config['description']}")
            lines.append("")
            
            # Tools
            tools = config.get("tools", [])
            if tools:
                lines.append("**Capabilities (Tools):**")
                for tool in tools:
                    # LangChain tools have .name and .description
                    tool_name = getattr(tool, "name", str(tool))
                    tool_desc = getattr(tool, "description", "No description")
                    lines.append(f"- `{tool_name}`: {tool_desc}")
            else:
                lines.append("*No external tools (Pure reasoning agent)*")
            
            lines.append("")
            lines.append("---")
            lines.append("")
            
        return "\n".join(lines)

    def generate_json_ld(self) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data
        """
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "MomentAIc",
            "description": "The Entrepreneur Operating System",
            "applicationCategory": "BusinessApplication",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "agents": [
                {
                    "@type": "Service",
                    "name": config["name"],
                    "description": config["description"]
                }
                for config in AGENT_CONFIGS.values()
            ]
        }

llm_context_service = LLMContextService()
