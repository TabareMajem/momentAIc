import os
from typing import Dict, List, Any
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agents.base import get_llm
from pydantic import BaseModel, Field
import json

class CampaignAsset(BaseModel):
    persona: str = Field(description="The target persona (e.g., Publishers, Advertisers, Agencies, SMB Producers)")
    language: str = Field(description="The language of the content (EN, ES, JP)")
    cold_email_subject: str = Field(description="A highly converting cold email subject line")
    cold_email_body: str = Field(description="The body of the cold email, strictly localized to cultural norms")
    linkedin_dm: str = Field(description="A short, punchy direct message for LinkedIn or Twitter")
    landing_page_hook: str = Field(description="A powerful H1 hook for a customized landing page")

class MultilingualMatrix(BaseModel):
    assets: List[CampaignAsset] = Field(description="A list of generated assets covering all required personas and languages")

class MultilingualCampaignAgent:
    def __init__(self):
        # We need a highly capable model for nuanced translation, so Gemini Pro or GPT-4o
        self.llm = get_llm("gemini-pro", temperature=0.7)
        self.parser = JsonOutputParser(pydantic_object=MultilingualMatrix)
        
        self.prompt = PromptTemplate(
            template="""You are an elite Global Growth Hacker and Localization Expert.
Your objective is to generate a massive outbound campaign matrix for a specific product.

TARGET PRODUCT DOMAIN: {domain}
REQUIREMENTS: {requirements}

TARGET PERSONAS:
{personas}

TARGET LANGUAGES:
{languages}

For EACH combination of Persona and Language, you must generate a highly customized suite of outbound marketing assets.

CRITICAL LOCALIZATION RULES:
- English (EN): Aggressive, direct, value-driven, "Silicon Valley" style.
- Spanish (ES): Warm, relationship-focused, professional but approachable (use 'usted' depending on context, aim for Latin American / International Spanish).
- Japanese (JP): Extreme respect (Keigo - 敬語), highly structured, honoring the recipient's status, apologizing for the cold outreach but presenting undeniable value. 

Analyze the core value proposition of "{domain}" and mold it perfectly for each persona's pain points.

{format_instructions}
""",
            input_variables=["domain", "requirements", "personas", "languages"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    async def generate_matrix(self, domain: str, personas: List[str], languages: List[str], additional_context: str = "") -> List[Dict[str, str]]:
        """
        Generates the full matrix of multilingual campaign assets.
        """
        personas_str = "\n".join([f"- {p}" for p in personas])
        languages_str = "\n".join([f"- {l}" for l in languages])
        
        reqs = "Generate 1 Cold Email Subject, 1 Cold Email Body, 1 LinkedIn DM, and 1 Landing Page Hook for every single combination of the provided personas and languages."
        if additional_context:
            reqs += f"\n\nADDITIONAL CONTEXT: {additional_context}"
            
        chain = self.prompt | self.llm | self.parser
        
        try:
            # We use invoke because this is a heavy single generation task.
            result = chain.invoke({
                "domain": domain,
                "requirements": reqs,
                "personas": personas_str,
                "languages": languages_str
            })
            
            # Extract the actual list of assets from the Pydantic wrapper structure
            if "assets" in result:
                return result["assets"]
            elif isinstance(result, list):
                return result
            else:
                return [result]
                
        except Exception as e:
            print(f"Error generating multilingual campaign matrix: {str(e)}")
            # Fallback if parsing completely fails
            return []
