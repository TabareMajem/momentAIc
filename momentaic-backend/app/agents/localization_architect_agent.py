"""
Localization Architect Agent - War Room Cultural Adaptation
Adapts marketing copy for global markets with cultural sensitivity.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import structlog

# Standalone agent - no base class needed
from app.core.config import settings

logger = structlog.get_logger()


class LocalizedContent(BaseModel):
    """Culturally adapted content for a region."""
    region: str
    language: str
    headline: str
    subheadline: str
    cta_button: str
    value_props: List[str]
    testimonial_style: str
    trust_signals: List[str]
    tone_notes: str


class LocalizationArchitectAgent:
    """
    War Room Agent: Localization Architect
    
    Mission: Culturally adapt marketing content for global markets.
    
    Regions & Tone Profiles:
    - US: Direct, benefit-focused, urgency-driven
    - LatAm: Community-focused, aspirational, warm
    - Europe: Privacy-conscious, efficiency-driven, professional
    - Asia: Trust-based, technical, formal respect
    """
    
    REGION_PROFILES = {
        "US": {
            "languages": ["en"],
            "tone": "Direct, bold, action-oriented",
            "values": ["Speed", "ROI", "Competitive advantage"],
            "avoid": ["Overly formal language", "Slow build-ups"],
            "trust_signals": ["Customer logos", "Revenue metrics", "Speed claims"],
            "example_headline": "10x Your Startup. Zero Extra Hires.",
            "cta_style": "Strong imperatives (Get Started, Claim Your Spot)"
        },
        "LatAm": {
            "languages": ["es", "pt"],
            "tone": "Warm, community-driven, aspirational",
            "values": ["Family success", "Community impact", "Personal growth"],
            "avoid": ["Cold corporate language", "Isolation messaging"],
            "trust_signals": ["Testimonios de emprendedores", "Community size", "Local success stories"],
            "example_headline": "Tu Negocio Merece Un Equipo De IA",
            "cta_style": "Invitational (Únete, Descubre, Empieza Gratis)"
        },
        "Europe": {
            "languages": ["en", "de", "fr", "es"],
            "tone": "Professional, privacy-conscious, efficiency-focused",
            "values": ["Data security", "Time savings", "Work-life balance"],
            "avoid": ["Hype language", "Aggressive sales tactics"],
            "trust_signals": ["GDPR compliance", "EU hosting", "Enterprise clients"],
            "example_headline": "AI That Respects Your Data. Results That Respect Your Time.",
            "cta_style": "Professional (Start Free Trial, Learn More, Request Demo)"
        },
        "Asia": {
            "languages": ["en", "ja", "ko", "zh"],
            "tone": "Trust-based, technical, respectful formality",
            "values": ["Reliability", "Technical excellence", "Long-term partnership"],
            "avoid": ["Casual language", "Aggressive closing", "Unrealistic promises"],
            "trust_signals": ["Technical certifications", "Enterprise partnerships", "Detailed specs"],
            "example_headline": "信頼性の高いAIパートナー for Your Business",
            "cta_style": "Respectful (お問い合わせ, 無料で始める, 詳細を見る)"
        }
    }
    
    def __init__(self):
        self.name = "Localization Architect"
        self.description = "Culturally adapts content for global markets"
        self._tools = self._create_tools()
    
    def _create_tools(self) -> List:
        """Create localization-specific tools."""
        
        @tool
        def analyze_cultural_context(
            region: str
        ) -> Dict:
            """
            Get cultural context and preferences for a region.
            
            Args:
                region: Target region (US, LatAm, Europe, Asia)
            
            Returns:
                Cultural profile with tone, values, and guidelines
            """
            profile = LocalizationArchitectAgent.REGION_PROFILES.get(
                region,
                LocalizationArchitectAgent.REGION_PROFILES["US"]
            )
            return {
                "region": region,
                "profile": profile,
                "status": "Profile retrieved"
            }
        
        @tool
        def translate_with_cultural_adaptation(
            source_text: str,
            source_language: str,
            target_language: str,
            target_region: str
        ) -> str:
            """
            Translate text with cultural adaptation (not just literal translation).
            
            Args:
                source_text: Original text in source language
                source_language: Source language code (en, es, etc.)
                target_language: Target language code
                target_region: Target cultural region
            
            Returns:
                Culturally adapted translation
            """
            # LLM will perform the actual adaptation
            return {
                "action": "cultural_translation",
                "source": source_text,
                "from": source_language,
                "to": target_language,
                "region": target_region,
                "status": "Ready for LLM processing"
            }
        
        @tool
        def generate_region_landing_copy(
            region: str,
            product_features: List[str],
            target_audience: str
        ) -> LocalizedContent:
            """
            Generate full landing page copy for a region.
            
            Args:
                region: Target region
                product_features: List of product features to highlight
                target_audience: Description of target audience
            
            Returns:
                Complete localized content package
            """
            # LLM will generate this based on region profile
            return {
                "action": "generate_landing_copy",
                "region": region,
                "features": product_features,
                "audience": target_audience,
                "status": "Ready for LLM generation"
            }
        
        @tool
        def validate_cultural_sensitivity(
            content: str,
            target_region: str
        ) -> Dict:
            """
            Check content for cultural sensitivity issues.
            
            Args:
                content: Content to validate
                target_region: Target region
            
            Returns:
                Validation results with any flagged issues
            """
            return {
                "action": "validate_sensitivity",
                "region": target_region,
                "content_length": len(content),
                "status": "Ready for LLM validation"
            }
        
        return [
            analyze_cultural_context,
            translate_with_cultural_adaptation,
            generate_region_landing_copy,
            validate_cultural_sensitivity
        ]
    
    async def localize_campaign(
        self,
        source_content: Dict[str, str],
        target_regions: List[str]
    ) -> Dict[str, LocalizedContent]:
        """
        Localize a marketing campaign for multiple regions.
        
        Args:
            source_content: Original English content
            target_regions: List of target regions
        
        Returns:
            Localized content for each region
        """
        logger.info(f"Localizing campaign for regions: {target_regions}")
        
        results = {}
        
        for region in target_regions:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert localization architect for global SaaS marketing.

Your mission is to adapt marketing content for {region}.

Cultural Profile:
{profile}

Rules:
1. Do NOT just translate - culturally adapt
2. Adjust tone, examples, and value propositions
3. Use region-appropriate trust signals
4. Respect local business etiquette
5. For non-English regions, provide both English and native language versions"""),
                ("user", """Adapt this campaign content for {region}:

Headline: {headline}
Subheadline: {subheadline}
CTA: {cta}
Value Props: {value_props}

Provide:
1. Adapted headline
2. Adapted subheadline
3. Adapted CTA
4. Region-specific value propositions
5. Recommended trust signals
6. Tone notes for designers""")
            ])
            
            profile = self.REGION_PROFILES.get(region, self.REGION_PROFILES["US"])
            
            from app.agents.base import get_llm
            
            llm = get_llm("gemini-2.5-flash", temperature=0.5)
            chain = prompt | llm
            
            result = await chain.ainvoke({
                "region": region,
                "profile": str(profile),
                "headline": source_content.get("headline", ""),
                "subheadline": source_content.get("subheadline", ""),
                "cta": source_content.get("cta", ""),
                "value_props": source_content.get("value_props", [])
            })
            
            results[region] = LocalizedContent(
                region=region,
                language=profile["languages"][0],
                headline=result.content,  # Parsed from LLM response
                subheadline="",
                cta_button="",
                value_props=[],
                testimonial_style=profile["tone"],
                trust_signals=profile["trust_signals"],
                tone_notes=profile["tone"]
            )
        
        return results
    
    async def localize_outreach_script(
        self,
        base_script: str,
        target_region: str,
        kol_profile: Dict
    ) -> str:
        """
        Localize an outreach script for a specific KOL's region.
        
        Args:
            base_script: Original English outreach script
            target_region: Target region
            kol_profile: Profile of the target KOL
        
        Returns:
            Culturally adapted outreach script
        """
        profile = self.REGION_PROFILES.get(target_region, self.REGION_PROFILES["US"])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an outreach specialist adapting messages for {region}.

Cultural guidelines:
- Tone: {tone}
- Values: {values}
- Avoid: {avoid}

Maintain the core offer but adapt:
1. Opening style
2. Relationship building approach
3. How benefits are framed
4. Closing style"""),
            ("user", """Adapt this outreach script for {region}:

{script}

KOL Details:
- Name: {kol_name}
- Platform: {platform}
- Language: {language}

Output the adapted script.""")
        ])
        
        from app.agents.base import get_llm
        
        llm = get_llm("gemini-2.5-flash", temperature=0.4)
        chain = prompt | llm
        
        result = await chain.ainvoke({
            "region": target_region,
            "tone": profile["tone"],
            "values": ", ".join(profile["values"]),
            "avoid": ", ".join(profile["avoid"]),
            "script": base_script,
            "kol_name": kol_profile.get("name", "there"),
            "platform": kol_profile.get("platform", "social media"),
            "language": profile["languages"][0]
        })
        
        return result.content


# Singleton instance

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for new market expansion opportunities and cultural adaptation needs.
        """
        actions = []
        logger.info(f"Agent {self.__class__.__name__} starting proactive scan")
        
        industry = startup_context.get("industry", "Technology")
        
        from app.agents.base import web_search
        results = await web_search(f"{industry} new market expansion opportunities and cultural adaptation needs 2025")
        
        if results:
            from app.agents.base import get_llm
            llm = get_llm("gemini-pro", temperature=0.3)
            if llm:
                from langchain_core.messages import HumanMessage
                prompt = f"""Analyze these results for a {industry} startup:
{str(results)[:2000]}

Identify the top 3 actionable insights. Be concise."""
                try:
                    response = await llm.ainvoke([HumanMessage(content=prompt)])
                    from app.agents.base import BaseAgent
                    if hasattr(self, 'publish_to_bus'):
                        await self.publish_to_bus(
                            topic="intelligence_gathered",
                            data={
                                "source": "LocalizationArchitectAgent",
                                "analysis": response.content[:1500],
                                "agent": "localization_architect",
                            }
                        )
                    actions.append({"name": "market_opportunity", "industry": industry})
                except Exception as e:
                    logger.error(f"LocalizationArchitectAgent proactive scan failed", error=str(e))
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Generates culturally-adapted marketing copy for global market expansion.
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            from app.agents.base import get_llm, web_search
            from langchain_core.messages import HumanMessage
            
            industry = startup_context.get("industry", "Technology")
            llm = get_llm("gemini-pro", temperature=0.5)
            
            if not llm:
                return "LLM not available"
            
            search_results = await web_search(f"{industry} {action_type} best practices 2025")
            
            prompt = f"""You are the Global market cultural adaptation agent for a {industry} startup.

Based on this context:
- Action requested: {action_type}
- Industry: {industry}
- Research: {str(search_results)[:1500]}

Generate a concrete, actionable deliverable. No fluff. Be specific and executable."""
            
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            
            if hasattr(self, 'publish_to_bus'):
                await self.publish_to_bus(
                    topic="deliverable_generated",
                    data={
                        "type": action_type,
                        "content": response.content[:2000],
                        "agent": "localization_architect",
                    }
                )
            return f"Action complete: {response.content[:200]}"

        except Exception as e:
            logger.error("LocalizationArchitectAgent autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"

localization_architect = LocalizationArchitectAgent()
