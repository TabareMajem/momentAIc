"""
Growth Hacker Agent
AI-powered growth expert for startups
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
    read_url_content,
    get_trending_topics,
    BaseAgent,
    safe_parse_json,
)
from app.models.conversation import AgentType

logger = structlog.get_logger()


class GrowthHackerAgent(BaseAgent):
    """
    Growth Hacker Agent - Expert in startup growth strategies
    
    Capabilities:
    - Growth experiment design
    - Acquisition channel analysis
    - Conversion funnel optimization
    - Retention strategies
    - Viral loop identification
    - A/B testing recommendations
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.GROWTH_HACKER)
        # Use valid model name for streaming
        self.llm = get_llm("gemini-2.0-flash", temperature=0.7)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a growth-related question or request
        """
        if not self.llm:
            return {"response": "Growth Hacker Agent not initialized (LLM missing).", "agent": AgentType.GROWTH_HACKER.value}

        prompt = f"""You are the Growth Hacker Agent.
        Context: {startup_context}
        Query: {message}
        
        Provide a detailed, actionable growth strategy or answer."""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return {"response": response.content, "agent": AgentType.GROWTH_HACKER.value}
        except Exception as e:
            logger.error("Growth Hacker agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}


    async def design_experiment(
        self,
        goal: str,
        current_metrics: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Design a growth experiment
        """
        constraints = constraints or {"budget": 0, "time": "1 week"}
        
        if not self.llm:
            return {"experiment_design": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Design a growth experiment:

Goal: {goal}

Current Metrics:
- DAU: {current_metrics.get('dau', 0):,}
- WAU: {current_metrics.get('wau', 0):,}
- Conversion Rate: {current_metrics.get('conversion_rate', 0)}%
- Churn: {current_metrics.get('churn', 0)}%

Constraints:
- Budget: ${constraints.get('budget', 0)}
- Time: {constraints.get('time', '1 week')}
- Team Size: {constraints.get('team_size', 1)}

Provide:
1. Experiment hypothesis
2. Specific tactics to test
3. Control vs variant setup
4. Success metrics
5. Statistical significance requirements
6. Implementation steps
7. Rollback plan"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "experiment_design": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Experiment design failed", error=str(e))
            return {"experiment_design": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def analyze_funnel(
        self,
        funnel_data: Dict[str, Any],
        industry: str = "SaaS",
    ) -> Dict[str, Any]:
        """
        Analyze conversion funnel and identify leaks
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "biggest_leak": "No Data", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Analyze this {industry} conversion funnel:

Funnel Steps:
- Visitors: {funnel_data.get('visitors', 0):,}
- Signups: {funnel_data.get('signups', 0):,} ({self._calc_rate(funnel_data.get('signups', 0), funnel_data.get('visitors', 1))}%)
- Activated: {funnel_data.get('activated', 0):,} ({self._calc_rate(funnel_data.get('activated', 0), funnel_data.get('signups', 1))}%)
- Retained (D7): {funnel_data.get('d7_retained', 0):,}
- Paid: {funnel_data.get('paid', 0):,}

Provide:
1. Biggest leak identification
2. Industry benchmark comparison
3. Top 3 optimization opportunities
4. Quick wins (implement in <1 day)
5. Strategic improvements (1-4 weeks)
6. Metrics to track improvements"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "biggest_leak": self._identify_biggest_leak(funnel_data),
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Funnel analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "biggest_leak": "Error", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def acquisition_channels(
        self,
        startup_context: Dict[str, Any],
        budget: int = 0,
    ) -> Dict[str, Any]:
        """
        Recommend acquisition channels
        """
        if not self.llm:
            return {"recommendations": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Recommend acquisition channels:

Startup:
- Industry: {startup_context.get('industry', 'Technology')}
- Target Customer: {startup_context.get('target_customer', 'B2B SMBs')}
- Price Point: ${startup_context.get('price_point', 50)}/month
- Current Stage: {startup_context.get('stage', 'MVP')}

Budget: ${budget:,}/month

Provide:
1. Top 5 recommended channels (ranked)
2. Expected CAC for each
3. Time to results
4. Effort required
5. Playbook for #1 channel
6. Channels to avoid at this stage"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "recommendations": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Channel analysis failed", error=str(e))
            return {"recommendations": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def viral_loop_design(
        self,
        product_type: str,
        current_k_factor: float = 0,
    ) -> Dict[str, Any]:
        """
        Design viral growth loops
        """
        if not self.llm:
            return {"viral_strategy": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Design viral growth loops for:

Product Type: {product_type}
Current K-factor: {current_k_factor}
Target K-factor: 1.0+

Provide:
1. Natural viral mechanics in your product
2. Incentive-based referral program design
3. Network effects to leverage
4. Viral content opportunities
5. Sharing friction reduction tactics
6. K-factor improvement roadmap"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "viral_strategy": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Viral loop design failed", error=str(e))
            return {"viral_strategy": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    async def retention_strategy(
        self,
        cohort_data: Dict[str, Any],
        product_type: str,
    ) -> Dict[str, Any]:
        """
        Design retention improvement strategy
        """
        if not self.llm:
            return {"retention_plan": "AI Service Unavailable", "agent": AgentType.GROWTH_HACKER.value, "error": True}
        
        prompt = f"""Design retention strategy:

Product: {product_type}

Retention Data:
- D1: {cohort_data.get('d1', 0)}%
- D7: {cohort_data.get('d7', 0)}%
- D30: {cohort_data.get('d30', 0)}%
- Monthly Churn: {cohort_data.get('monthly_churn', 0)}%

Provide:
1. Retention curve analysis
2. Critical drop-off points
3. Engagement triggers to implement
4. Re-engagement campaign ideas
5. Onboarding optimization
6. 90-day retention roadmap"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "retention_plan": response.content,
                "agent": AgentType.GROWTH_HACKER.value,
            }
        except Exception as e:
            logger.error("Retention strategy failed", error=str(e))
            return {"retention_plan": f"Error: {str(e)}", "agent": AgentType.GROWTH_HACKER.value, "error": True}
    
    def _build_context(self, startup_context: Dict[str, Any]) -> str:
        """Build startup context"""
        return f"""Startup Context:
- Name: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- MRR: ${startup_context.get('metrics', {}).get('mrr', 0):,}
- DAU: {startup_context.get('metrics', {}).get('dau', 0):,}"""
    
    def _calc_rate(self, numerator: int, denominator: int) -> str:
        """Calculate percentage rate"""
        if denominator == 0:
            return "0"
        return f"{(numerator / denominator) * 100:.1f}"
        
    async def analyze_startup_wizard(self, url: str, description: str = "") -> Dict[str, Any]:
        """
        One-Shot Wizard Analysis: Generates complete GTM strategy from URL/Description.
        Used for 60-Second Result onboarding.
        """
        if not self.llm:
            return {"error": "Growth Hacker Agent not initialized"}
            
        import json
        
        # [REALITY UPGRADE] Scrape the URL if provided
        scraped_content = ""
        if url and "http" in url:
            try:
                from app.agents.browser_agent import browser_agent
                logger.info(f"GrowthHacker: Scraping {url} for wizard analysis")
                result = await browser_agent.navigate(url)
                if result.success:
                    scraped_content = f"\n\nWEBSITE CONTENT ({url}):\n{result.text_content[:8000]}"
                else:
                    scraped_content = f"\n\nWEBSITE CONTENT: Failed to scrape {url}. Error: {result.error}"
            except Exception as e:
                logger.error(f"Scraping failed for {url}", error=str(e))
        
        prompt = f"""
        Analyze this startup for a "60-Second Growth Strategy":
        URL: {url}
        Description: {description}
        {scraped_content}
        
        If the URL is valid, infer what the company does from the WEBSITE CONTENT. If description is provided, use it.
        
        You must generate a structured JSON strategy with:
        1. "target_audience": The single most lucrative initial customer segment.
        2. "pain_point": Their bleeding neck problem.
        3. "value_prop": The killer hook.
        4. "viral_post_hook": A contrarian or curiosity-driven hook.
        5. "weekly_goal": A concrete first-week metric.
        6. "yc_application": A nested object with "problem", "solution", "secret_sauce", "why_now", answering typical Y combinator application questions concisely.
        
        Format as purely JSON:
        {{
            "target_audience": "...",
            "pain_point": "...",
            "value_prop": "...",
            "viral_post_hook": "...",
            "weekly_goal": "...",
            "yc_application": {{
                "problem": "...",
                "solution": "...",
                "secret_sauce": "...",
                "why_now": "..."
            }}
        }}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content
            
            parsed = safe_parse_json(content)
            if parsed:
                return parsed
            else:
                return {
                    "target_audience": "Early Adopters",
                    "pain_point": "Unknown problem",
                    "value_prop": "Innovative solution",
                    "viral_post_hook": "We are launching something new!",
                    "weekly_goal": "Get 100 visitors",
                    "yc_application": {
                        "problem": "Not yet analyzed.",
                        "solution": "Not yet analyzed.",
                        "secret_sauce": "Not yet analyzed.",
                        "why_now": "Not yet analyzed."
                    }
                }
        except Exception as e:
            logger.error("Wizard analysis failed", error=str(e))
            return {"error": str(e)}

    def _identify_biggest_leak(self, funnel: Dict[str, Any]) -> str:
        """Identify biggest conversion drop"""
        steps = [
            ("visitor→signup", funnel.get('signups', 0) / max(funnel.get('visitors', 1), 1)),
            ("signup→activated", funnel.get('activated', 0) / max(funnel.get('signups', 1), 1)),
            ("activated→retained", funnel.get('d7_retained', 0) / max(funnel.get('activated', 1), 1)),
            ("retained→paid", funnel.get('paid', 0) / max(funnel.get('d7_retained', 1), 1)),
        ]
        return min(steps, key=lambda x: x[1])[0]
    
    async def monitor_social(
        self,
        keywords: List[str],
        platform: str = "reddit",
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Monitor social platforms for discussions relevant to the startup and draft replies.
        """
        if not self.llm:
            return {"error": "Growth Hacker Agent not initialized"}
            
        try:
            results = []
            
            # 1. Search for discussions
            base_query = " OR ".join(keywords)
            search_query = f"site:{platform}.com {base_query} after:2024-01-01"
            logger.info("GrowthHacker: Monitoring social", platform=platform, query=search_query)
            
            # Use async invoke for the tool
            search_text = await web_search.ainvoke(search_query)
            
            # 2. Parse URLs (Simple regex or LLM extraction)
            import re
            urls = re.findall(r'https?://[^\s\)]+', search_text)[:limit]
            
            if not urls:
                return {"message": "No recent discussions found.", "opportunities": []}
                
            logger.info("GrowthHacker: Found discussions", count=len(urls))
            
            # 3. Analyze each thread and draft reply
            opportunities = []
            for url in urls:
                try:
                    # Read thread content
                    content = await read_url_content.ainvoke(url)
                    if "Failed" in content:
                        continue
                        
                    # Draft detailed reply
                    prompt = f"""
                    You are a helpful expert (not a spam bot).
                    
                    Thread Content:
                    {content[:10000]}
                    
                    Task: 
                    1. Analyze if this thread is relevant to our keywords: {keywords}.
                    2. If relevant, draft a genuinely helpful reply that adds value first, and subtly mentions our solution if appropriate.
                    3. If not relevant, return "SKIP".
                    
                    Format: JSON
                    {{
                        "relevant": true/false,
                        "summary": "Thread summary...",
                        "draft_reply": "Hey OP, I ran into this too...",
                        "sentiment": "positive/negative/neutral"
                    }}
                    """
                    
                    analysis_msg = await self.llm.ainvoke([HumanMessage(content=prompt)])
                    analysis_text = analysis_msg.content
                    
                    data = safe_parse_json(analysis_text)
                    if data and data.get("relevant"):
                            opportunities.append({
                                "url": url,
                                "summary": data.get("summary"),
                                "draft_reply": data.get("draft_reply"),
                                "status": "drafted"
                            })
                            
                except Exception as e:
                    logger.warning(f"Failed to process thread {url}", error=str(e))
            
            return {
                "platform": platform,
                "keywords": keywords,
                "opportunities": opportunities,
                "agent": AgentType.GROWTH_HACKER.value
            }

        except Exception as e:
            logger.error("Social monitoring failed", error=str(e))
            return {"error": str(e)}

    # ==== TWIN.SO KILLER: ANALYTICS FEATURES ====
    
    async def weekly_growth_report(
        self,
        startup_context: Dict[str, Any],
        metrics: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate automated weekly growth insights.
        Superior to twin.so: AI-powered actionable recommendations.
        """
        metrics = metrics or {}
        
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        prompt = f"""Generate a weekly growth report for this startup:

STARTUP: {startup_context.get('name', 'Unknown')}
INDUSTRY: {startup_context.get('industry', 'Tech')}

THIS WEEK'S METRICS:
- Website Visitors: {metrics.get('visitors', 0)}
- Signups: {metrics.get('signups', 0)}
- Active Users: {metrics.get('dau', 0)}
- Revenue: ${metrics.get('revenue', 0)}
- Social Followers: {metrics.get('followers', 0)}

LAST WEEK'S METRICS:
- Visitors: {metrics.get('prev_visitors', 0)}
- Signups: {metrics.get('prev_signups', 0)}

Generate a report with:
1. Week-over-Week Growth Summary
2. Top 3 Wins This Week
3. Top 3 Opportunities Missed
4. Priority Actions for Next Week (be SPECIFIC)
5. Growth Score (1-100)

Format as JSON."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            parsed = safe_parse_json(response.content)
            if parsed:
                return {
                    "success": True,
                    "report": parsed,
                    "generated_at": datetime.now().isoformat(),
                    "agent": AgentType.GROWTH_HACKER.value
                }
            return {"raw_report": response.content}
        except Exception as e:
            logger.error("Weekly report generation failed", error=str(e))
            return {"error": str(e)}

    async def audience_heatmap(
        self,
        past_engagement: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze best posting times based on past engagement.
        Returns a heatmap of optimal posting hours by day.
        """
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        # If no data, return defaults
        if not past_engagement:
            return {
                "success": True,
                "heatmap": {
                    "monday": [9, 12, 17],
                    "tuesday": [10, 14, 18],
                    "wednesday": [9, 12, 17],
                    "thursday": [10, 14, 18],
                    "friday": [9, 12, 15],
                    "saturday": [10, 14],
                    "sunday": [11, 15],
                },
                "best_overall": "Tuesday 10am, Thursday 2pm",
                "source": "industry_defaults"
            }
        
        prompt = f"""Analyze this engagement data and find the best posting times:

ENGAGEMENT DATA:
{past_engagement[:50]}

Return a JSON heatmap:
{{
    "heatmap": {{
        "monday": [best_hours],
        "tuesday": [best_hours],
        ...
    }},
    "best_overall": "Day Time, Day Time",
    "worst_times": "Day Time",
    "insights": "..."
}}"""

        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            parsed = safe_parse_json(response.content)
            if parsed:
                return {"success": True, **parsed}
            return {"raw": response.content}
        except Exception as e:
            return {"error": str(e)}

    async def competitor_content_spy(
        self,
        competitor_handles: List[str],
        platform: str = "linkedin",
    ) -> Dict[str, Any]:
        """
        Spy on competitor content strategy.
        Identifies what's working for them that you should steal.
        """
        if not self.llm:
            return {"error": "LLM not initialized"}
        
        try:
            competitor_data = []
            for handle in competitor_handles[:3]:
                # Search for their recent posts
                query = f"site:{platform}.com/in/{handle} OR site:{platform}.com/company/{handle}"
                results = await web_search.ainvoke(query)
                competitor_data.append({"handle": handle, "results": results})
            
            prompt = f"""Analyze these competitor social profiles:

{competitor_data}

Identify:
1. Their top content themes
2. Posting frequency
3. Engagement tactics
4. Hashtags they use
5. What YOU should steal/adapt

Format as JSON with 'steal_this' array."""

            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            parsed = safe_parse_json(response.content)
            if parsed:
                return {"success": True, **parsed}
            return {"raw": response.content}
        except Exception as e:
            return {"error": str(e)}


# Import datetime for reports
from datetime import datetime


    # ── AUTONOMOUS PROACTIVITY ───────────────────────────────────────

class _GrowthHackerProactiveMixin:
    """Mixin added to GrowthHackerAgent below for proactive scanning."""
    
    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively identify growth opportunities:
        - Scan trending topics in the startup's industry
        - Propose social monitoring sweeps for Reddit/HN
        - Suggest weekly growth reports
        """
        actions = []
        industry = startup_context.get("industry", "Technology")
        
        # 1. Trending topic scan for content opportunities
        try:
            trends = await get_trending_topics.ainvoke({"industry": industry, "platform": "twitter"})
            if trends and isinstance(trends, list) and len(trends) > 0:
                actions.append({
                    "action": "generate_trend_content",
                    "name": "trend_content",
                    "description": f"Generate content around trending topic: {trends[0]}",
                    "priority": "high",
                    "agent": "GrowthHackerAgent",
                    "topic": trends[0] if isinstance(trends[0], str) else str(trends[0]),
                })
        except Exception as e:
            logger.warning("GrowthHacker proactive trend scan failed", error=str(e))
        
        # 2. Social monitoring sweep (Reddit, HN)
        keywords = [
            startup_context.get("name", ""),
            industry,
            startup_context.get("description", "")[:30],
        ]
        keywords = [k for k in keywords if k]
        
        if keywords:
            actions.append({
                "action": "social_monitor",
                "name": "reddit_monitor",
                "description": f"Monitor Reddit/HN for discussions about: {', '.join(keywords[:3])}",
                "priority": "medium",
                "agent": "GrowthHackerAgent",
                "keywords": keywords[:3],
            })
        
        # 3. Weekly growth report
        actions.append({
            "action": "weekly_report",
            "name": "growth_report",
            "description": "Generate weekly growth report with metrics analysis and recommendations.",
            "priority": "low",
            "agent": "GrowthHackerAgent",
        })
        
        if actions:
            await self.publish_to_bus(
                topic="growth_opportunities_found",
                data={"summary": f"Found {len(actions)} growth opportunities", "count": len(actions)},
            )
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute a proactive growth action using REAL services.
        """
        action_type = action.get("action", action.get("name", "unknown"))
        agent_name = "GrowthHackerAgent"
        
        try:
            if action_type == "generate_trend_content":
                # Generate real content about the trending topic
                from app.agents.content_agent import content_agent
                from app.models.growth import ContentPlatform
                
                topic = action.get("topic", startup_context.get("industry", "Technology"))
                result = await content_agent.generate(
                    platform=ContentPlatform.LINKEDIN,
                    topic=topic,
                    startup_context=startup_context,
                    content_type="post",
                    tone="professional",
                    trend_based=False,
                )
                
                if result.get("success"):
                    # Schedule the generated content for posting
                    from app.services.social_scheduler import social_scheduler
                    content_body = result.get("content", {}).get("full_body", "")
                    if content_body:
                        post = await social_scheduler.schedule_post(
                            startup_id=startup_context.get("id", startup_context.get("startup_id", "")),
                            content=content_body,
                            platforms=["linkedin"],
                            scheduled_at=datetime.utcnow(),
                        )
                        return f"Content generated and scheduled for LinkedIn (post_id: {post.id})"
                    return f"Content generated but empty body: {result}"
                return f"Content generation failed: {result.get('error', 'unknown')}"
                    
            elif action_type == "social_monitor":
                # Run real social monitoring
                keywords = action.get("keywords", [startup_context.get("industry", "tech")])
                result = await self.monitor_social(keywords=keywords, platform="reddit", limit=3)
                opportunities = result.get("opportunities", [])
                return f"Social monitor found {len(opportunities)} relevant discussions"
                
            elif action_type == "weekly_report":
                # Generate real weekly report
                result = await self.weekly_growth_report(startup_context=startup_context)
                if result.get("success"):
                    return f"Weekly growth report generated successfully"
                return f"Report generation incomplete: {result.get('error', 'no data')}"

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: 2025/2026 Growth-Strategy Actions
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            elif action_type == "plg_funnel_audit":
                # Product-Led Growth: analyze signup-to-activation funnel
                if self.llm:
                    metrics = startup_context.get("metrics", {})
                    prompt = f"""You are a Product-Led Growth expert auditing {startup_context.get('name', 'this startup')}.

Industry: {startup_context.get('industry', 'SaaS')}
Current Metrics:
- Visitors/mo: {metrics.get('visitors', 'N/A')}
- Signup Rate: {metrics.get('signup_rate', 'N/A')}%
- Activation Rate: {metrics.get('activation_rate', 'N/A')}%
- Time to Value: {metrics.get('time_to_value', 'N/A')}

Perform a comprehensive PLG audit:

1. **Friction Points**: Identify the top 5 friction points in signup → activation
2. **Quick Wins**: 3 changes that can be implemented in <1 day to improve activation
3. **Self-Serve Blockers**: What prevents users from getting value without human help?
4. **Aha Moment Analysis**: What's the likely "aha moment"? How fast do users reach it?
5. **Free-to-Paid Conversion**: Optimal paywall placement and pricing trigger points
6. **Benchmark Comparison**: Compare to industry PLG benchmarks (Slack, Notion, Figma patterns)

Format as structured JSON with actionable recommendations."""

                    response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                    parsed = safe_parse_json(response.content)

                    await self.publish_to_bus(
                        topic="plg_audit_complete",
                        data={"summary": "PLG funnel audit completed with actionable recommendations", "audit": parsed or response.content[:500]},
                        target_agents=["ContentAgent", "SDRAgent"],
                    )
                    return f"PLG funnel audit completed for {startup_context.get('name', 'startup')}"
                return "LLM not available"

            elif action_type == "viral_loop_designer":
                # Design referral/invite mechanics based on the startup's product type
                if self.llm:
                    product_type = startup_context.get("description", startup_context.get("industry", "SaaS"))
                    prompt = f"""You are a viral growth engineer. Design a complete viral loop system for:

Product: {startup_context.get('name', 'this product')}
Type: {product_type[:200]}
Industry: {startup_context.get('industry', 'SaaS')}

Design 3 viral loop mechanisms:

**Loop 1: Built-in Viral (Product-Native)**
- What action naturally shares the product?
- How to amplify it (e.g., "Made with [Product]" watermarks, shared workspaces)
- Expected K-factor improvement

**Loop 2: Incentive-Based Referral**
- Reward structure (2-sided: referrer + referee)
- Optimal reward type (credits, features, cash)
- Friction-minimized sharing flow (1-click)

**Loop 3: Content Viral**
- User-generated content that promotes the product
- Templates/tools that users share naturally
- Social proof mechanics

For each loop:
- Implementation effort (Low/Med/High)
- Expected K-factor contribution
- Time to first results

Format as structured JSON."""

                    response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                    parsed = safe_parse_json(response.content)
                    return f"Viral loop system designed: {str(parsed)[:300] if parsed else response.content[:300]}"
                return "LLM not available"

            elif action_type == "expansion_revenue_finder":
                # Identify upsell opportunities from usage data
                if self.llm:
                    metrics = startup_context.get("metrics", {})
                    prompt = f"""You are a revenue expansion specialist for {startup_context.get('name', 'this SaaS')}.

Current Metrics:
- MRR: ${metrics.get('mrr', 0)}
- Active Customers: {metrics.get('customers', 0)}
- ARPU: ${metrics.get('arpu', 0)}
- Industry: {startup_context.get('industry', 'SaaS')}

Identify expansion revenue opportunities:

1. **Usage-Based Upsells**: What usage thresholds should trigger upgrade prompts?
2. **Feature Gating Strategy**: Which features should be premium vs free?
3. **Seat Expansion**: How to encourage team-wide adoption (land-and-expand)?
4. **Add-On Products**: What complementary products/services can be offered?
5. **Annual Plan Incentives**: Optimal discount for annual commitment
6. **Enterprise Tier Design**: What separates a $50/mo plan from a $500/mo plan?

For each opportunity, estimate:
- Revenue impact (% MRR increase)
- Implementation complexity
- Time to revenue

Format as JSON with priorities ranked by effort-to-impact ratio."""

                    response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                    parsed = safe_parse_json(response.content)

                    await self.publish_to_bus(
                        topic="expansion_opportunities_found",
                        data={"summary": "Expansion revenue opportunities identified", "opportunities": parsed or response.content[:500]},
                        target_agents=["FinanceCFOAgent", "SDRAgent"],
                    )
                    return f"Expansion revenue opportunities identified for {startup_context.get('name', 'startup')}"
                return "LLM not available"
                
            else:
                return f"Unknown action type: {action_type}"
                
        except Exception as e:
            logger.error(f"{agent_name} autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"


# Apply the mixin to GrowthHackerAgent
GrowthHackerAgent.proactive_scan = _GrowthHackerProactiveMixin.proactive_scan
GrowthHackerAgent.autonomous_action = _GrowthHackerProactiveMixin.autonomous_action

# Singleton instance
growth_hacker_agent = GrowthHackerAgent()
