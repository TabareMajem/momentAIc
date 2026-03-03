"""
HR & Operations Agent
AI-powered HR and operations advisor
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, BaseAgent, web_search
from app.models.conversation import AgentType
from app.services.deliverable_service import deliverable_service

logger = structlog.get_logger()


class HROperationsAgent(BaseAgent):
    """
    HR & Operations Agent - Expert in people operations and org building
    
    Capabilities:
    - Job description generation
    - Interview question design
    - Onboarding checklists
    - Team structure recommendations
    - Compensation benchmarking
    - Culture documentation
    - Proactive talent market scanning
    """
    
    def __init__(self):
        self.name = "HR Operations Agent"
        self.llm = get_llm("gemini-pro", temperature=0.6)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process an HR/operations question"""
        if not self.llm:
            return {"response": "AI Service Unavailable. Please configure keys.", "agent": "hr_operations", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As HR/Operations expert, provide:
1. Practical recommendations
2. Best practices
3. Templates or frameworks
4. Common pitfalls to avoid
5. Next steps"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "hr_operations",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("HR Operations agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "hr_operations", "error": True}
    
    async def generate_job_description(
        self,
        role: str,
        level: str,
        requirements: List[str],
    ) -> Dict[str, Any]:
        """Generate a job description"""
        if not self.llm:
            return {"job_description": "AI Service Unavailable", "agent": "hr_operations", "error": True}
        
        prompt = f"""Create job description:

Role: {role}
Level: {level}
Requirements: {', '.join(requirements)}

Include:
1. Compelling job title
2. About the company section
3. Role responsibilities (5-7 bullets)
4. Required qualifications
5. Nice-to-have skills
6. Benefits and perks
7. How to apply"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "job_description": response.content,
                "agent": "hr_operations",
            }
        except Exception as e:
            logger.error("JD generation failed", error=str(e))
            return {"job_description": f"Error: {str(e)}", "agent": "hr_operations", "error": True}
    
    async def create_interview_questions(
        self,
        role: str,
        competencies: List[str],
    ) -> Dict[str, Any]:
        """Create interview questions"""
        if not self.llm:
            return {"questions": "AI Service Unavailable", "agent": "hr_operations", "error": True}
        
        prompt = f"""Create interview questions for: {role}

Competencies to assess: {', '.join(competencies)}

Provide:
1. Phone screen questions (3)
2. Technical/skill questions (5)
3. Behavioral questions (5)
4. Culture fit questions (3)
5. Candidate questions to expect
6. Red flags to watch for"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "questions": response.content,
                "agent": "hr_operations",
            }
        except Exception as e:
            logger.error("Interview questions failed", error=str(e))
            return {"questions": f"Error: {str(e)}", "agent": "hr_operations", "error": True}
    
    async def create_onboarding_plan(
        self,
        role: str,
        remote: bool = True,
    ) -> Dict[str, Any]:
        """Create an onboarding checklist"""
        if not self.llm:
            return {"onboarding_plan": "AI Service Unavailable", "agent": "hr_operations", "error": True}
        
        work_type = "remote" if remote else "in-office"
        prompt = f"""Create {work_type} onboarding plan for: {role}

Include:
1. Pre-start checklist
2. Day 1 agenda
3. Week 1 milestones
4. 30-day goals
5. 60-day goals
6. 90-day success criteria
7. Key people to meet"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "onboarding_plan": response.content,
                "agent": "hr_operations",
            }
        except Exception as e:
            logger.error("Onboarding plan failed", error=str(e))
            return {"onboarding_plan": f"Error: {str(e)}", "agent": "hr_operations", "error": True}
    
    async def recommend_org_structure(
        self,
        team_size: int,
        stage: str,
    ) -> Dict[str, Any]:
        """Recommend organizational structure"""
        if not self.llm:
            return {"recommendation": "AI Service Unavailable", "agent": "hr_operations", "error": True}
        
        prompt = f"""Recommend org structure:

Team Size: {team_size}
Stage: {stage}

Provide:
1. Recommended structure
2. Key roles to hire first
3. Reporting lines
4. When to add management layers
5. Common mistakes at this stage"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendation": response.content,
                "agent": "hr_operations",
            }
        except Exception as e:
            logger.error("Org structure failed", error=str(e))
            return {"recommendation": f"Error: {str(e)}", "agent": "hr_operations", "error": True}

    async def generate_recruiting_packet(
        self,
        company_name: str,
        role: str,
        requirements: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a recruiting packet (JD + Search Strings) as a downloadable file.
        """
        try:
            # 1. Generate content via LLM
            jd_content = await self.generate_job_description(role, "Mid-Senior", requirements)
            text_content = jd_content.get("job_description", "")
            
            # 2. Add search strings
            search_strings = f"\n\n=== RECRUITER SEARCH STRINGS ===\n"
            search_strings += f'site:linkedin.com/in/ "{role}" AND ({" OR ".join(requirements[:3])}) AND "{company_name.split()[0]}"'
            
            full_content = text_content + search_strings
            
            # 3. Create PDF via DeliverableService (reusing legal contract logic or adding text-to-pdf)
            # For now, we'll piggyback on generate_business_plan_pdf structure or add a generic one.
            # Let's assume we add a generic text-to-pdf to deliverable service or just use the plan one with different title.
            
            content_dict = {
                "executive_summary": f"Job Description: {role}\n\n" + full_content,
                "market_analysis": "",
                "growth_strategy": "",
                "financial_projections": ""
            }
            
            # Using generate_business_plan_pdf as a generic PDF generator for now (hacky but works for MVP)
            # Ideally verify deliverable_service has a generic text_to_pdf
            result = await deliverable_service.generate_business_plan_pdf(content_dict, f"{company_name}_{role}_JD")
            
            return {
                "file_url": result["url"],
                "file_type": "PDF",
                "title": f"Recruiting Packet: {role}",
                "agent": "hr_operations"
            }
        except Exception as e:
            logger.error("Recruiting packet generation failed", error=str(e))
            return {"error": str(e), "agent": "hr_operations"}
    
    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for talent market trends and hiring opportunities.
        Searches for salary benchmarks, hiring trends, and competitor job postings.
        """
        actions = []
        logger.info(f"Agent {self.name} starting proactive talent scan")
        
        industry = startup_context.get("industry", "Technology")
        stage = startup_context.get("stage", "Seed")
        
        # 1. Search for hiring trends in this industry
        results = await web_search(f"{industry} startup hiring trends salaries 2025")
        
        if results and self.llm:
            prompt = f"""Analyze these hiring market results for a {stage}-stage {industry} startup:
{str(results)[:2000]}

Provide:
1. Key hiring trends in this space
2. Salary ranges for critical roles
3. Hiring recommendations for this stage
4. Talent pool availability assessment"""
            
            try:
                response = await self.llm.ainvoke([
                    SystemMessage(content=self._get_system_prompt()),
                    HumanMessage(content=prompt),
                ])
                
                await self.publish_to_bus(
                    topic="talent_market_intel",
                    data={
                        "industry": industry,
                        "analysis": response.content[:1500],
                        "agent": "hr_operations",
                    }
                )
                actions.append({"name": "talent_market_scanned", "industry": industry})
            except Exception as e:
                logger.error("HR proactive scan failed", error=str(e))
        
        # 2. Check competitor job postings
        company_name = startup_context.get("name", "")
        competitors = startup_context.get("competitors", [])
        if competitors:
            comp = competitors[0] if isinstance(competitors[0], str) else competitors[0].get("name", "")
            comp_results = await web_search(f"{comp} job openings hiring 2025")
            if comp_results:
                from app.models.action_item import ActionPriority
                await self.publish_to_bus(
                    topic="action_item_proposed",
                    data={
                        "action_type": "competitor_hiring_alert",
                        "title": f"🔍 Competitor Hiring: {comp} has open roles",
                        "description": f"Competitor {comp} is actively hiring. Consider talent poaching or competitive positioning.",
                        "payload": {"competitor": comp, "results": [r.get("title", "") for r in comp_results[:3]]},
                        "priority": ActionPriority.low.value
                    }
                )
                actions.append({"name": "competitor_hiring_detected", "competitor": comp})
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute HR autonomous actions:
        - Auto-generate job descriptions for critical roles
        - Create recruiting packets
        - Generate onboarding plans
        """
        action_type = action.get("action", action.get("name", "unknown"))

        try:
            if action_type in ("talent_market_scanned", "generate_jd"):
                # Auto-generate JD for the most needed role
                industry = startup_context.get("industry", "Technology")
                stage = startup_context.get("stage", "Seed")
                
                if self.llm:
                    prompt = f"""For a {stage}-stage {industry} startup, identify the single most critical hire right now and generate a complete job description.

Consider: What role would have the highest impact on growth at this stage?

Provide the full JD with title, responsibilities, requirements, and benefits."""
                    response = await self.llm.ainvoke([
                        SystemMessage(content=self._get_system_prompt()),
                        HumanMessage(content=prompt),
                    ])
                    
                    await self.publish_to_bus(
                        topic="deliverable_generated",
                        data={
                            "type": "job_description",
                            "content": response.content[:2000],
                            "agent": "hr_operations",
                        }
                    )
                    return f"Critical hire JD generated: {response.content[:200]}"
                return "LLM not available"

            elif action_type in ("competitor_hiring_detected", "onboarding_plan"):
                # Generate onboarding template
                if self.llm:
                    prompt = f"""Create a universal first-week onboarding plan for a {startup_context.get('stage', 'Seed')}-stage startup.

Include:
1. Pre-arrival setup (tools, accounts)
2. Day 1: Welcome, culture, team introductions
3. Day 2-3: Product deep-dive, codebase/system walkthrough
4. Day 4-5: First meaningful task, buddy system setup
5. Week 1 success criteria"""
                    response = await self.llm.ainvoke([
                        SystemMessage(content=self._get_system_prompt()),
                        HumanMessage(content=prompt),
                    ])
                    return f"Onboarding plan generated: {response.content[:200]}"
                return "LLM not available"

            else:
                return f"Unknown action type: {action_type}"

        except Exception as e:
            logger.error("HR autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        return """You are the HR & Operations agent - expert in startup people ops.

Your expertise:
- Hiring and recruitment
- Onboarding and training
- Team structure and org design
- Culture and values
- Compensation and benefits
- Remote work best practices

Focus on practical, startup-appropriate advice.
Avoid enterprise-level complexity for early-stage companies."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        return f"""Startup Context:
- Name: {ctx.get('name', 'Unknown')}
- Stage: {ctx.get('stage', 'Early Stage')}
- Team Size: {ctx.get('metrics', {}).get('team_size', 1)}"""
    


# Singleton
hr_operations_agent = HROperationsAgent()
