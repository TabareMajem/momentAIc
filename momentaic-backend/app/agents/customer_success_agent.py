"""
Customer Success Agent
AI-powered customer success manager
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import structlog

from app.agents.base import get_llm, get_agent_config, web_search
from app.models.conversation import AgentType

logger = structlog.get_logger()


class CustomerSuccessAgent:
    """
    Customer Success Agent - Expert in customer retention and satisfaction
    
    Capabilities:
    - Churn risk analysis
    - Customer health scoring
    - Success playbooks
    - Onboarding optimization
    - QBR preparation
    - Upsell identification
    """
    
    def __init__(self):
        self.llm = get_llm("gemini-pro", temperature=0.6)
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Process a customer success question"""
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": "customer_success", "error": True}
        
        try:
            context = self._build_context(startup_context)
            prompt = f"""{context}

User Request: {message}

As Customer Success expert, provide:
1. Direct actionable advice
2. Customer health considerations
3. Retention strategies
4. Metrics to track
5. Playbook recommendations"""

            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": "customer_success",
                "tools_used": [],
            }
        except Exception as e:
            logger.error("Customer Success agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": "customer_success", "error": True}
    
    async def analyze_churn_risk(
        self,
        customer_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze churn risk for a customer"""
        risk_score = self._calculate_risk_score(customer_data)
        
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "risk_score": risk_score, "agent": "customer_success", "error": True}
        
        prompt = f"""Analyze churn risk:

Customer Data:
- Last login: {customer_data.get('last_login', 'Unknown')}
- Usage trend: {customer_data.get('usage_trend', 'Unknown')}
- Support tickets: {customer_data.get('support_tickets', 0)}
- NPS score: {customer_data.get('nps', 'Not collected')}
- Account age: {customer_data.get('account_age_months', 0)} months

Calculated Risk Score: {risk_score}/100

Provide:
1. Risk assessment
2. Warning signs
3. Immediate actions
4. Re-engagement strategy"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "analysis": response.content,
                "risk_score": risk_score,
                "agent": "customer_success",
            }
        except Exception as e:
            logger.error("Churn analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "risk_score": risk_score, "agent": "customer_success", "error": True}
    
    async def create_success_playbook(
        self,
        customer_segment: str,
        goals: List[str],
    ) -> Dict[str, Any]:
        """Create a customer success playbook"""
        if not self.llm:
            return {"playbook": "AI Service Unavailable", "agent": "customer_success", "error": True}
        
        prompt = f"""Create success playbook for:

Segment: {customer_segment}
Goals: {', '.join(goals)}

Include:
1. Onboarding milestones (first 30/60/90 days)
2. Success metrics per milestone
3. Touchpoint schedule
4. Health check triggers
5. Escalation procedures
6. Expansion opportunities"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=prompt),
            ])
            
            return {
                "playbook": response.content,
                "agent": "customer_success",
            }
        except Exception as e:
            logger.error("Playbook creation failed", error=str(e))
            return {"playbook": f"Error: {str(e)}", "agent": "customer_success", "error": True}
    
    async def triage_ticket(self, ticket_content: str, sender_sentiment: str = "neutral") -> Dict[str, Any]:
        """Classify a support ticket and draft a reply"""
        if not self.llm:
            return {"classification": "error", "draft": "Service Unavailable"}
            
        prompt = f"""Triage this support ticket:
"{ticket_content}"
(Sentiment: {sender_sentiment})

Output JSON:
1. "priority": High/Medium/Low
2. "category": Technical/Billing/Feature/Other
3. "draft_reply": Empathetic and helpful response (max 100 words)
4. "action_required": Internal action needed if any
"""
        try:
            from langchain_core.output_parsers import JsonOutputParser
            chain = self.llm | JsonOutputParser()
            result = await chain.ainvoke([HumanMessage(content=prompt)])
            return result
        except Exception as e:
             # Fallback parsing
            return {"priority": "Medium", "category": "General", "draft_reply": "Thank you for your message. We are looking into it.", "item": str(e)}
    
    def _get_system_prompt(self) -> str:
        return """You are the Customer Success agent - expert in customer retention.

Your expertise:
- Churn prediction and prevention
- Customer health scoring
- Onboarding optimization
- NPS and satisfaction management
- Upsell and expansion strategies

Focus on proactive engagement and data-driven decisions."""
    
    def _build_context(self, ctx: Dict[str, Any]) -> str:
        metrics = ctx.get('metrics', {})
        return f"""Startup Context:
- Product: {ctx.get('name', 'Unknown')}
- Industry: {ctx.get('industry', 'SaaS')}
- Churn rate: {metrics.get('churn', 'Unknown')}%
- NPS: {metrics.get('nps', 'Unknown')}"""
    
    def _calculate_risk_score(self, data: Dict[str, Any]) -> int:
        """Calculate churn risk score (0-100, higher = more risk)"""
        score = 30  # Base
        
        # Usage decline
        if data.get('usage_trend') == 'declining':
            score += 25
        
        # Support issues
        tickets = data.get('support_tickets', 0)
        if tickets > 5:
            score += 20
        elif tickets > 2:
            score += 10
        
        # Low NPS
        nps = data.get('nps')
        if nps and nps < 6:
            score += 25
        
        return min(100, score)

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively scan for customer success risks:
        - Detect customers with declining usage
        - Identify high-risk accounts needing intervention
        - Propose re-engagement campaigns
        """
        actions = []
        metrics = startup_context.get("metrics", {})
        churn_rate = metrics.get("churn", metrics.get("churn_rate", 0))
        nps = metrics.get("nps", 50)
        
        # 1. High churn rate → re-engagement campaign
        if churn_rate and float(churn_rate) > 5:
            actions.append({
                "action": "churn_prevention",
                "name": "churn_prevention",
                "description": f"Churn rate at {churn_rate}% — generate re-engagement campaign.",
                "priority": "urgent",
                "agent": "CustomerSuccessAgent",
                "churn_rate": churn_rate,
            })
        
        # 2. Low NPS → satisfaction survey and outreach
        if nps and float(nps) < 30:
            actions.append({
                "action": "nps_recovery",
                "name": "nps_recovery",
                "description": f"NPS at {nps} — launch satisfaction recovery program.",
                "priority": "high",
                "agent": "CustomerSuccessAgent",
                "nps": nps,
            })
        
        # 3. Weekly success review
        actions.append({
            "action": "weekly_success_review",
            "name": "success_review",
            "description": "Generate weekly customer success review with health scores.",
            "priority": "medium",
            "agent": "CustomerSuccessAgent",
        })
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute a proactive customer success action using REAL services.
        """
        action_type = action.get("action", action.get("name", "unknown"))
        
        try:
            if action_type == "churn_prevention":
                # Generate re-engagement playbook
                churn_rate = action.get("churn_rate", "unknown")
                result = await self.create_success_playbook(
                    customer_segment="at-risk",
                    goals=["Reduce churn", "Improve engagement", "Increase NPS"],
                )
                
                if result.get("playbook"):
                    from app.services.activity_stream import activity_stream
                    await activity_stream.publish(
                        startup_id=startup_context.get("id", ""),
                        event_type="agent_action",
                        title=f"🛡️ Churn Prevention Playbook Generated",
                        description=f"Churn at {churn_rate}%. Re-engagement playbook created.",
                        agent="CustomerSuccessAgent",
                    )
                    # ── EMAIL PLAYBOOK TO FOUNDER ───────────────────
                    try:
                        from app.services.notification_service import notification_service
                        from app.integrations.gmail import gmail_integration
                        from app.core.config import settings as app_settings
                        
                        await notification_service.dispatch_agent_alert(
                            startup_id=startup_context.get("id"),
                            agent_name="CustomerSuccessAgent",
                            channel="email",
                            dispatch_func=gmail_integration.execute_action,
                            action="send_email",
                            params={
                                "to": startup_context.get("founder_email", getattr(app_settings, "GMAIL_USER", "")),
                                "subject": f"🛡️ Churn Prevention Playbook — {startup_context.get('name', 'Startup')}",
                                "body": result.get('playbook', '')[:5000],
                                "priority": "normal",
                                "agent_name": "Customer Success Agent"
                            }
                        )
                    except Exception:
                        pass
                    # ── SLACK ALERT ───────────────────────────────────
                    try:
                        from app.services.notification_service import notification_service
                        from app.integrations.slack import SlackIntegration
                        slack = SlackIntegration()
                        
                        await notification_service.dispatch_agent_alert(
                            startup_id=startup_context.get("id"),
                            agent_name="CustomerSuccessAgent",
                            channel="slack",
                            dispatch_func=slack.execute_action,
                            action="send_message",
                            params={
                                "channel": "#general",
                                "text": f"🛡️ *Churn Alert — {startup_context.get('name', 'Startup')}*\nChurn at {churn_rate}%. Playbook generated and emailed.",
                            }
                        )
                    except Exception:
                        pass
                    return f"Churn prevention playbook generated for {churn_rate}% churn rate"
                return "Playbook generation failed"
            
            elif action_type == "nps_recovery":
                # Generate NPS recovery plan
                if self.llm:
                    prompt = f"""Create a specific NPS recovery plan for {startup_context.get('name', 'our startup')}.
Current NPS: {action.get('nps', 'low')}
                    
Generate:
1. Root cause analysis framework
2. 5 immediate actions to improve NPS
3. Follow-up survey template
4. 30-day recovery timeline"""
                    response = await self.llm.ainvoke(prompt)
                    return f"NPS recovery plan generated: {response.content[:200]}"
                return "LLM not available"
            
            elif action_type == "weekly_success_review":
                # Generate weekly health report
                if self.llm:
                    prompt = f"""Generate a weekly Customer Success review for {startup_context.get('name', 'our startup')}.
Industry: {startup_context.get('industry', 'SaaS')}
Churn: {startup_context.get('metrics', {}).get('churn', 'N/A')}%
NPS: {startup_context.get('metrics', {}).get('nps', 'N/A')}

Provide: Top 3 risks, Top 3 opportunities, and 3 action items."""
                    response = await self.llm.ainvoke(prompt)
                    return f"Weekly success review generated: {response.content[:200]}"
                return "LLM not available"

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: Revenue Retention Machine (NRR >120%)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            elif action_type == "customer_health_scoring":
                # Calculate per-customer health scores from usage + payment + support signals
                if self.llm:
                    customers_data = action.get("customers", [])
                    prompt = f"""You are a Customer Success analytics engine for {startup_context.get('name', 'this SaaS')}.
Industry: {startup_context.get('industry', 'SaaS')}

Calculate health scores for these customers based on available signals:
{str(customers_data)[:3000]}

For each customer, generate:
1. Health Score (0-100): 0=churning, 100=champion
2. Risk Level: Low/Medium/High/Critical
3. Key Signal: The #1 indicator driving the score
4. Recommended Action: Specific next step for CS team
5. Expansion Readiness: Yes/No + reason

Scoring Framework:
- Usage Frequency (+20 pts): Active daily = 20, weekly = 12, monthly = 5
- Feature Adoption (+20 pts): Using >80% features = 20, >50% = 12, <30% = 5
- Support Tickets (+15 pts): 0 tickets = 15, 1-2 = 10, 3+ = 3
- Payment Health (+15 pts): Always on-time = 15, 1 late = 8, failed = 0
- Engagement Trend (+15 pts): Growing = 15, Stable = 10, Declining = 3
- NPS/Feedback (+15 pts): Promoter = 15, Passive = 8, Detractor = 0

Format as JSON array: [{{"customer": "...", "score": 85, "risk": "Low", "signal": "...", "action": "...", "expansion_ready": true}}]"""

                    response = await self.llm.ainvoke(prompt)
                    from app.agents.base import safe_parse_json
                    scored = safe_parse_json(response.content)

                    # Publish to agent bus for cross-agent awareness
                    at_risk = [c for c in (scored or []) if isinstance(c, dict) and c.get("risk") in ("High", "Critical")]
                    if at_risk:
                        await self.publish_to_bus(
                            topic="at_risk_customers_identified",
                            data={"summary": f"{len(at_risk)} at-risk customers identified", "customers": at_risk},
                            target_agents=["FinanceCFOAgent", "SDRAgent"],
                        )

                    return f"Health scores calculated for {len(scored) if isinstance(scored, list) else 0} customers, {len(at_risk)} at-risk"
                return "LLM not available"

            elif action_type == "churn_prediction":
                # Predict at-risk customers 30 days ahead and auto-trigger rescue playbooks
                if self.llm:
                    metrics = startup_context.get("metrics", {})
                    churn_rate = metrics.get("churn", 0)

                    prompt = f"""You are a churn prediction AI for {startup_context.get('name', 'this SaaS')}.
Industry: {startup_context.get('industry', 'SaaS')}
Current Monthly Churn: {churn_rate}%
MRR: ${metrics.get('mrr', 0)}

Based on typical {startup_context.get('industry', 'SaaS')} churn patterns, predict:

1. **30-Day Churn Forecast**: Expected churn rate and revenue impact
2. **Early Warning Signals**: Top 5 behavioral signals that predict churn 30 days before it happens
3. **Rescue Playbook**: For each churn signal, provide an automated rescue sequence:
   - Day 1: What email/notification to send
   - Day 3: What action to take if no response
   - Day 7: Escalation step
   - Day 14: Last resort offer
4. **Preventive Measures**: 3 proactive changes to reduce baseline churn
5. **Win-Back Sequence**: For already-churned customers, a 3-email win-back sequence

Format as structured JSON."""

                    response = await self.llm.ainvoke(prompt)
                    parsed = safe_parse_json(response.content)

                    # Alert founder if churn is concerning
                    if churn_rate and float(churn_rate) > 5:
                        try:
                            from app.services.notification_service import notification_service
                            from app.integrations.slack import SlackIntegration
                            slack = SlackIntegration()
                            await notification_service.dispatch_agent_alert(
                                startup_id=startup_context.get("id"),
                                agent_name="CustomerSuccessAgent",
                                channel="slack",
                                dispatch_func=slack.execute_action,
                                action="send_message",
                                params={
                                    "channel": "#customer-success",
                                    "text": f"⚠️ *Churn Prediction Alert — {startup_context.get('name')}*\nCurrent churn: {churn_rate}%. Rescue playbooks generated.",
                                },
                            )
                        except Exception:
                            pass

                    return f"Churn prediction generated: forecast + rescue playbooks (current churn: {churn_rate}%)"
                return "LLM not available"

            elif action_type == "expansion_opportunity":
                # Identify power users ready for upsell
                if self.llm:
                    prompt = f"""You are an expansion revenue specialist for {startup_context.get('name', 'this SaaS')}.

Industry: {startup_context.get('industry', 'SaaS')}
Current ARPU: ${startup_context.get('metrics', {}).get('arpu', 0)}

Identify expansion opportunities:

1. **Power User Profile**: What behavioral patterns indicate a user is ready for an upgrade?
2. **Usage Ceiling Triggers**: At what usage level should we trigger "you're outgrowing your plan" messages?
3. **Team Expansion Signals**: When should we suggest adding team seats?
4. **Feature Discovery**: How to expose premium features to free users without being pushy?
5. **Upgrade Conversation Templates**: 3 email templates for different upgrade scenarios:
   - Usage limit approaching
   - Feature request for premium feature
   - Team growth detected

Format as structured JSON."""

                    response = await self.llm.ainvoke(prompt)
                    parsed = safe_parse_json(response.content)

                    await self.publish_to_bus(
                        topic="expansion_opportunities_detected",
                        data={"summary": "Power users identified for expansion", "opportunities": parsed or response.content[:500]},
                        target_agents=["SDRAgent", "FinanceCFOAgent"],
                    )
                    return f"Expansion opportunities identified for {startup_context.get('name', 'startup')}"
                return "LLM not available"
            
            else:
                return f"Unknown action type: {action_type}"
                
        except Exception as e:
            logger.error("CustomerSuccess autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"


# Singleton
customer_success_agent = CustomerSuccessAgent()
