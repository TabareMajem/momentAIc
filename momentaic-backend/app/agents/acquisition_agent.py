from typing import Dict, Any, List, Optional
import json
import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

logger = structlog.get_logger()

class AcquisitionAgent:
    """
    Acquisition Agent - Paid Media Specialist.
    Generates ad copy, targeting strategies, and creative concepts.
    """
    
    def __init__(self):
        # Using Gemini Flash for speed and cost
        self.llm = ChatGoogleGenerativeAI(
             model="gemini-1.5-flash",
             google_api_key=settings.google_api_key, 
             temperature=0.7
        )
    
    async def generate_ad_campaign(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a paid ad campaign strategy.
        """
        prompt = ChatPromptTemplate.from_template("""
        You are a world-class Performance Marketer.
        Design a paid acquisition campaign for this startup:
        
        Name: {name}
        Description: {description}
        Industry: {industry}
        Target Audience: {target_audience}
        
        Output a JSON object with this EXACT structure (no markdown):
        {{
            "platform": "Facebook/LinkedIn/Google",
            "strategy": "Strategy hook",
            "primary_text": "Ad copy (max 280 chars)",
            "headline": "Ad headline (max 40 chars)",
            "targeting": ["keyword1", "keyword2"],
            "creative_idea": "Visual description"
        }}
        
        Focus on high conversion.
        """)
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            result = await chain.ainvoke({
                "name": context.get("name"),
                "description": context.get("description"),
                "industry": context.get("industry"),
                "target_audience": context.get("target_audience", "SaaS Founders") 
            })
            return result
        except Exception as e:
            logger.error("AcquisitionAgent: Failed", error=str(e))
            return {"error": str(e)}

acquisition_agent = AcquisitionAgent()
