import structlog
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

from app.agents.base import get_llm

logger = structlog.get_logger()

class LeadMagnetGenerator:
    """
    Dynamic JSON Blueprint Generator
    
    Instead of sending static PDFs, this service uses DeepSeek to autonomously 
    write technically valid `.json` export files (e.g. n8n workflow nodes, 
    Make.com scenarios, or PostgreSQL schemas) perfectly tailored to the 
    prospect's exact tech stack, as requested via DMs.
    """
    
    def __init__(self):
        # We enforce "deepseek-chat" (V3) or "deepseek-reasoner" (R1) for this
        # because generating valid, complex JSON syntax requires top-tier reasoning.
        self.llm = get_llm("deepseek-chat", temperature=0.7)
        self.output_dir = Path("/root/momentaic/momentaic-backend/data/blueprints")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_n8n_blueprint(self, prospect_context: str, specific_request: str) -> Dict[str, Any]:
        """Synthesizes a valid n8n workflow JSON file based on the conversation"""
        
        if not self.llm:
            return {"success": False, "error": "LLM Service Unavailable"}
            
        logger.info("generating_dynamic_n8n_blueprint", context=prospect_context)
        
        prompt = f"""You are the Lead Solutions Architect for Symbiotask.
A high-value prospect has requested an architecture blueprint from our outreach campaign.

PROSPECT CONTEXT:
{prospect_context}

SPECIFIC REQUEST:
{specific_request}

YOUR TASK:
Generate a fully valid, syntactically correct `n8n` workflow JSON export.
The workflow should demonstrate the "Symbiotask Frame Consistency Check" or "PostgreSQL auto-resume" logic mentioned in the campaign, tailored to their request.

REQUIREMENTS:
1. It MUST be valid JSON.
2. It MUST follow the n8n export schema (nodes array, connections object).
3. Include at least 3 nodes (Webhook trigger, HTTP Request to Symbiotask API, and a Postgres/Data transformation node).
4. Output ONLY the raw JSON string. DO NOT wrap it in ```json blocks or include any conversational text.
"""
        try:
            response = await self.llm.ainvoke(prompt)
            raw_json_str = response.content.strip()
            
            # Clean possible markdown block formatting from LLM
            if raw_json_str.startswith("```json"):
                raw_json_str = raw_json_str[7:]
            if raw_json_str.endswith("```"):
                raw_json_str = raw_json_str[:-3]
            raw_json_str = raw_json_str.strip()
                
            # Validate Syntax
            workflow_data = json.loads(raw_json_str)
            
            # Save file physically for the BrowserAgent to upload
            filename = f"symbiotask_blueprint_{hash(prospect_context)}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(workflow_data, f, indent=2)
                
            return {
                "success": True,
                "filepath": str(filepath),
                "type": "n8n_workflow",
                "preview": raw_json_str[:200]
            }
            
        except json.JSONDecodeError as e:
            logger.error("blueprint_json_validation_failed", error=str(e), raw_output=raw_json_str[:500])
            return {"success": False, "error": "LLM failed to generate valid JSON schema"}
        except Exception as e:
            logger.error("blueprint_generation_failed", error=str(e))
            return {"success": False, "error": str(e)}

lead_magnet_generator = LeadMagnetGenerator()
