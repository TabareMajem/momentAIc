"""
Finance CFO Agent
LangGraph-based financial advisor and fundraising expert
"""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import structlog
import re

from app.agents.base import (
    AgentState,
    get_llm,
    get_agent_config,
    web_search,
    BaseAgent,
)
from app.models.conversation import AgentType
from app.services.deliverable_service import deliverable_service
from app.services.live_data_service import live_data_service

logger = structlog.get_logger()


class FinanceCFOAgent(BaseAgent):
    """
    Finance CFO Agent - Expert in startup finance and fundraising
    
    Capabilities:
    - Financial metrics analysis (MRR, ARR, burn rate, runway)
    - Unit economics calculation
    - Fundraising strategy and pitch advice
    - Financial projections
    - Investor readiness assessment
    - Benchmarking against industry standards
    """
    
    def __init__(self):
        self.config = get_agent_config(AgentType.FINANCE_CFO)
        self.llm = get_llm("gemini-pro", temperature=0.3)  # Lower temp for precision
    
    async def process(
        self,
        message: str,
        startup_context: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process a financial question or request
        """
        if not self.llm:
            return {"response": "AI Service Unavailable", "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        try:
            # Build financial context
            metrics = startup_context.get('metrics', {})
            context_section = self._build_context(startup_context, metrics)
            
            prompt = f"""{context_section}

User Request: {message}

As the Finance CFO, provide:
1. Direct answer with specific numbers where possible
2. Financial implications
3. Key metrics to track
4. Actionable recommendations
5. Risk considerations

Be precise with calculations and always explain the business impact."""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "response": response.content,
                "agent": AgentType.FINANCE_CFO.value,
                "tools_used": [],
            }
            
        except Exception as e:
            logger.error("Finance CFO agent error", error=str(e))
            return {"response": f"Error: {str(e)}", "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def analyze_metrics(
        self,
        metrics: Dict[str, Any],
        industry: str = "SaaS",
    ) -> Dict[str, Any]:
        """
        Analyze startup financial metrics
        """
        if not self.llm:
            return {"analysis": "AI Service Unavailable", "health_score": 0, "calculated_metrics": {}, "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        prompt = f"""Analyze these startup metrics for a {industry} company:

Current Metrics:
- MRR: ${metrics.get('mrr', 0):,}
- ARR: ${metrics.get('mrr', 0) * 12:,}
- Burn Rate: ${metrics.get('burn_rate', 0):,}/month
- Runway: {metrics.get('runway_months', 0)} months
- DAU: {metrics.get('dau', 0):,}
- CAC: ${metrics.get('cac', 0)}
- LTV: ${metrics.get('ltv', 0)}
- Churn: {metrics.get('churn', 0)}%

Provide:
1. Health assessment (1-10 score)
2. Key strengths
3. Areas of concern
4. Benchmark comparison
5. Top 3 priorities
6. 90-day improvement targets"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            health_score = self._calculate_health_score(metrics)
            
            return {
                "analysis": response.content,
                "health_score": health_score,
                "calculated_metrics": self._calculate_derived_metrics(metrics),
                "agent": AgentType.FINANCE_CFO.value,
            }
        except Exception as e:
            logger.error("Metrics analysis failed", error=str(e))
            return {"analysis": f"Error: {str(e)}", "health_score": 0, "calculated_metrics": {}, "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def fundraising_readiness(
        self,
        metrics: Dict[str, Any],
        target_raise: int,
        stage: str = "Seed",
    ) -> Dict[str, Any]:
        """
        Assess fundraising readiness
        """
        if not self.llm:
            return {"assessment": "AI Service Unavailable", "readiness_score": 0, "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        prompt = f"""Assess fundraising readiness:

Target Raise: ${target_raise:,}
Stage: {stage}

Current Metrics:
- MRR: ${metrics.get('mrr', 0):,}
- Growth Rate: {metrics.get('growth_rate', 0)}% MoM
- Runway: {metrics.get('runway_months', 0)} months
- Team Size: {metrics.get('team_size', 1)}

Provide:
1. Readiness score (1-100)
2. Implied valuation range
3. What investors will ask about
4. Gaps to address before raising
5. Recommended fundraising timeline
6. Alternative funding options to consider"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            return {
                "assessment": response.content,
                "readiness_score": self._calculate_readiness_score(metrics, target_raise),
                "agent": AgentType.FINANCE_CFO.value,
            }
        except Exception as e:
            logger.error("Fundraising assessment failed", error=str(e))
            return {"assessment": f"Error: {str(e)}", "readiness_score": 0, "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def create_projection(
        self,
        current_metrics: Dict[str, Any],
        months: int = 12,
        scenario: str = "base",  # base, optimistic, pessimistic
    ) -> Dict[str, Any]:
        """
        Create financial projections
        """
        if not self.llm:
            return {"narrative": "AI Service Unavailable", "projections": [], "agent": AgentType.FINANCE_CFO.value, "error": True}
        
        prompt = f"""Create {months}-month financial projection ({scenario} case):

Starting Point:
- MRR: ${current_metrics.get('mrr', 0):,}
- Burn Rate: ${current_metrics.get('burn_rate', 0):,}/month
- Growth Rate: {current_metrics.get('growth_rate', 10)}% MoM

Provide:
1. Month-by-month MRR projection
2. Break-even point (if applicable)
3. Total cash needed
4. Key assumptions
5. Sensitivity analysis
6. Major milestones to hit"""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=self.config["system_prompt"]),
                HumanMessage(content=prompt),
            ])
            
            projections = self._calculate_projections(current_metrics, months, scenario)
            
            return {
                "narrative": response.content,
                "projections": projections,
                "agent": AgentType.FINANCE_CFO.value,
            }
        except Exception as e:
            logger.error("Projection failed", error=str(e))
            return {"narrative": f"Error: {str(e)}", "projections": [], "agent": AgentType.FINANCE_CFO.value, "error": True}
    
    async def generate_financial_model_file(
        self,
        company_name: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a downloadable financial model (CSV) with LIVE benchmarks.
        """
        try:
            # 1. Fetch live market data
            multiples = await live_data_service.get_saas_multiples()
            
            # Inject into metrics for the CSV
            metrics["valuation_multiple"] = multiples["median_arr_multiple"]
            metrics["valuation_note"] = f"Based on live SaaS index: {multiples['median_arr_multiple']}x ARR"
            
            # 2. Generate the file via service
            result = await deliverable_service.generate_financial_model_csv(metrics, company_name)
            
            return {
                "file_url": result["url"],
                "file_type": result["type"],
                "title": f"{result['title']} (Live Data)",
                "agent": AgentType.FINANCE_CFO.value,
                "benchmarks": multiples
            }
        except Exception as e:
            logger.error("Financial model generation failed", error=str(e))
            return {"error": str(e), "agent": AgentType.FINANCE_CFO.value}

    def _build_context(self, startup_context: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Build financial context"""
        return f"""Startup Financial Context:
- Name: {startup_context.get('name', 'Unknown')}
- Industry: {startup_context.get('industry', 'Technology')}
- Stage: {startup_context.get('stage', 'MVP')}
- MRR: ${metrics.get('mrr', 0):,}
- Burn Rate: ${metrics.get('burn_rate', 0):,}/month
- Runway: {metrics.get('runway_months', 'Unknown')} months"""
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate overall financial health score (1-100)"""
        score = 50  # Base score
        
        # Runway bonus
        runway = metrics.get('runway_months', 0)
        if runway >= 18:
            score += 20
        elif runway >= 12:
            score += 10
        elif runway < 6:
            score -= 20
        
        # Growth bonus
        growth = metrics.get('growth_rate', 0)
        if growth >= 20:
            score += 15
        elif growth >= 10:
            score += 10
        elif growth < 0:
            score -= 15
        
        # Unit economics
        ltv = metrics.get('ltv', 0)
        cac = metrics.get('cac', 1)
        if cac > 0 and ltv / cac >= 3:
            score += 15
        
        return max(0, min(100, score))
    
    def _calculate_derived_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived financial metrics"""
        mrr = metrics.get('mrr', 0)
        burn = metrics.get('burn_rate', 0)
        cac = metrics.get('cac', 0)
        ltv = metrics.get('ltv', 0)
        
        return {
            "arr": mrr * 12,
            "ltv_cac_ratio": round(ltv / cac, 2) if cac > 0 else None,
            "months_to_profitability": round(burn / (mrr * 0.8)) if mrr > 0 else None,
            "gross_burn": burn,
            "net_burn": burn - mrr,
        }
    
    def _calculate_readiness_score(self, metrics: Dict[str, Any], target: int) -> int:
        """Calculate fundraising readiness score"""
        score = 0
        
        mrr = metrics.get('mrr', 0)
        growth = metrics.get('growth_rate', 0)
        
        # MRR relative to raise
        if mrr * 100 >= target:  # 100x multiple
            score += 30
        elif mrr * 50 >= target:
            score += 20
        else:
            score += 10
        
        # Growth rate
        if growth >= 20:
            score += 30
        elif growth >= 10:
            score += 20
        else:
            score += 10
        
        # Team
        if metrics.get('team_size', 1) >= 3:
            score += 20
        else:
            score += 10
        
        # Runway
        if metrics.get('runway_months', 0) >= 6:
            score += 20
        else:
            score += 5
        
        return min(100, score)
    
    def _calculate_projections(
        self, metrics: Dict[str, Any], months: int, scenario: str
    ) -> List[Dict[str, Any]]:
        """Calculate month-by-month projections"""
        mrr = metrics.get('mrr', 0)
        growth_rates = {
            "pessimistic": 0.05,
            "base": 0.10,
            "optimistic": 0.20,
        }
        growth = growth_rates.get(scenario, 0.10)
        
        projections = []
        current_mrr = mrr
        
        for month in range(1, months + 1):
            current_mrr = current_mrr * (1 + growth)
            projections.append({
                "month": month,
                "mrr": round(current_mrr, 2),
                "arr": round(current_mrr * 12, 2),
            })
        
        return projections

    async def proactive_scan(self, startup_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Proactively monitor financial health.
        Checks MRR trends, burn rate, and runway to alert the founder early.
        """
        actions = []
        logger.info("Agent FinanceCFOAgent starting proactive financial scan")
        
        metrics = startup_context.get("metrics", {})
        mrr = metrics.get("mrr", 0)
        burn_rate = metrics.get("burn_rate", 0)
        runway_months = metrics.get("runway_months", 0)
        prev_mrr = metrics.get("prev_mrr", 0)
        churn_rate = metrics.get("churn_rate", 0)
        
        from app.models.action_item import ActionPriority
        
        # 1. MRR Decline Alert
        if prev_mrr > 0 and mrr < prev_mrr:
            decline_pct = round(((prev_mrr - mrr) / prev_mrr) * 100, 1)
            await self.publish_to_bus(
                topic="action_item_proposed",
                data={
                    "action_type": "financial_alert",
                    "title": f"📉 MRR Declined {decline_pct}%: ${mrr:,.0f} → was ${prev_mrr:,.0f}",
                    "description": f"Monthly Recurring Revenue dropped by {decline_pct}%. Review churn and expansion revenue.",
                    "payload": {"mrr": mrr, "prev_mrr": prev_mrr, "decline_pct": decline_pct},
                    "priority": ActionPriority.high.value
                }
            )
            actions.append({"name": "mrr_declining", "decline_pct": decline_pct})
        
        # 2. Runway Warning
        if 0 < runway_months <= 6:
            await self.publish_to_bus(
                topic="action_item_proposed",
                data={
                    "action_type": "financial_alert",
                    "title": f"🔥 Runway Warning: {runway_months} months remaining",
                    "description": f"At current burn rate (${burn_rate:,.0f}/mo), you have {runway_months} months of runway. Consider fundraising or cost cuts.",
                    "payload": {"runway_months": runway_months, "burn_rate": burn_rate},
                    "priority": ActionPriority.urgent.value if runway_months <= 3 else ActionPriority.high.value
                }
            )
            actions.append({"name": "burn_rate_warning", "runway_months": runway_months})
        
        # 3. High Churn Alert
        if churn_rate > 5:  # >5% monthly churn is dangerous
            await self.publish_to_bus(
                topic="action_item_proposed",
                data={
                    "action_type": "financial_alert",
                    "title": f"⚠️ High Churn: {churn_rate}% monthly",
                    "description": f"Monthly churn rate is {churn_rate}%. Industry average is 3-5%. Investigate customer satisfaction.",
                    "payload": {"churn_rate": churn_rate},
                    "priority": ActionPriority.high.value
                },
                target_agents=["CXGuardianAgent", "SalesAgent"]
            )
            actions.append({"name": "high_churn_alert", "churn_rate": churn_rate, "action": "churn_analysis"})
        
        return actions

    async def autonomous_action(self, action: Dict[str, Any], startup_context: Dict[str, Any]) -> str:
        """
        Execute a proactive financial action using REAL services.
        """
        action_type = action.get("action", action.get("name", "unknown"))
        
        try:
            if action_type == "mrr_declining":
                # Pull real Stripe data for analysis
                try:
                    from app.integrations.stripe import stripe_service
                    stripe_data = await stripe_service.sync_data()
                    real_mrr = stripe_data.get("mrr", action.get("decline_pct", 0))
                    
                    # Generate analysis with real data
                    metrics = startup_context.get("metrics", {})
                    metrics["mrr"] = real_mrr
                    result = await self.analyze_metrics(metrics=metrics)
                    
                    await self.publish_to_bus(
                        topic="financial_analysis_complete",
                        data={"summary": f"MRR decline analysis: health score {result.get('health_score', 'N/A')}/100"},
                        target_agents=["SalesAgent", "CustomerSuccessAgent"],
                    )
                    # ── SLACK ALERT ────────────────────────────────────
                    try:
                        from app.services.notification_service import notification_service
                        from app.integrations.slack import SlackIntegration
                        slack = SlackIntegration()
                        
                        await notification_service.dispatch_agent_alert(
                            startup_id=startup_context.get("id"),
                            agent_name="FinanceCFOAgent",
                            channel="slack",
                            dispatch_func=slack.execute_action,
                            action="send_message",
                            params={
                                "channel": "#general",
                                "text": f"🚨 *MRR Decline Alert — {startup_context.get('name', 'Startup')}*\nHealth Score: {result.get('health_score', 'N/A')}/100. Sales and CS agents have been auto-dispatched.",
                            }
                        )
                    except Exception:
                        pass
                    return f"MRR decline analysis complete: health score {result.get('health_score', 'N/A')}/100"
                except Exception as e:
                    return f"Stripe data pull failed, analysis skipped: {str(e)}"
            
            elif action_type == "burn_rate_warning":
                # Generate projections showing when runway hits zero
                metrics = startup_context.get("metrics", {})
                result = await self.create_projection(current_metrics=metrics, months=12, scenario="pessimistic")
                
                await self.publish_to_bus(
                    topic="runway_projection_generated",
                    data={"summary": f"Runway projection generated: {action.get('runway_months', 'N/A')} months remaining"},
                )
                # ── SLACK ALERT ────────────────────────────────────
                try:
                    from app.services.notification_service import notification_service
                    from app.integrations.slack import SlackIntegration
                    slack = SlackIntegration()
                    
                    await notification_service.dispatch_agent_alert(
                        startup_id=startup_context.get("id"),
                        agent_name="FinanceCFOAgent",
                        channel="slack",
                        dispatch_func=slack.execute_action,
                        action="send_message",
                        params={
                            "channel": "#general",
                            "text": f"⚠️ *Burn Rate Warning — {startup_context.get('name', 'Startup')}*\nRunway: {action.get('runway_months', 'N/A')} months remaining. Pessimistic projection generated.",
                        }
                    )
                except Exception:
                    pass
                return f"Runway projection generated for {action.get('runway_months', 'N/A')} months remaining"
            
            elif action_type in ("high_churn_alert", "churn_analysis"):
                # Alert Customer Success agent
                churn_rate = action.get("churn_rate", 0)
                await self.publish_to_bus(
                    topic="churn_alert_dispatched",
                    data={"summary": f"High churn alert: {churn_rate}%", "churn_rate": churn_rate},
                    target_agents=["CustomerSuccessAgent", "SalesAgent"],
                )
                return f"Churn alert dispatched to CustomerSuccess and Sales agents ({churn_rate}%)"

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # NEW: Stripe-Powered Actions
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            elif action_type == "failed_payment_retry":
                invoice_id = action.get("invoice_id")
                customer_email = action.get("customer_email", "Unknown")
                amount = action.get("amount", 0)

                # Try to auto-retry the payment via Stripe
                retry_result = None
                try:
                    from app.integrations.stripe import StripeIntegration
                    stripe = StripeIntegration()
                    retry_result = await stripe.execute_action("retry_failed_payment", {"invoice_id": invoice_id})
                except Exception as retry_err:
                    logger.warning("Auto-retry failed", error=str(retry_err))

                # Alert the founder via email
                try:
                    from app.services.notification_service import notification_service
                    from app.integrations.gmail import gmail_integration

                    retry_status = "✅ Auto-retried successfully" if retry_result and retry_result.get("success") else "⚠️ Auto-retry failed — manual intervention needed"

                    await notification_service.dispatch_agent_alert(
                        startup_id=startup_context.get("id"),
                        agent_name="FinanceCFOAgent",
                        channel="email",
                        dispatch_func=gmail_integration.execute_action,
                        action="send_email",
                        params={
                            "to": startup_context.get("founder_email", ""),
                            "subject": f"💳 Payment Failed — {customer_email} (${amount:.2f})",
                            "body": f"""
<h3>Payment Failure Detected</h3>
<p><strong>Customer:</strong> {customer_email}</p>
<p><strong>Amount:</strong> ${amount:.2f}</p>
<p><strong>Invoice:</strong> {invoice_id}</p>
<p><strong>Auto-Recovery:</strong> {retry_status}</p>
<hr>
<p>Your CFO Agent detected this in real-time via Stripe webhooks. 
If auto-retry succeeded, no action needed. If not, consider reaching out to the customer.</p>
""",
                            "priority": "urgent",
                            "agent_name": "FinanceCFOAgent",
                            "severity": "critical",
                        },
                    )
                except Exception:
                    pass

                return f"Failed payment handled for {customer_email} (${amount:.2f}) — retry: {retry_result}"

            elif action_type == "revenue_anomaly_detected":
                event = action.get("event", "unknown")
                customer_id = action.get("customer_id", "Unknown")
                mrr_impact = action.get("mrr_impact", 0)
                amount_refunded = action.get("amount_refunded", 0)

                detail = f"Subscription canceled (MRR impact: ${abs(mrr_impact):.2f}/mo)" if event == "subscription_canceled" \
                    else f"Charge refunded: ${amount_refunded:.2f}"

                # Alert via Slack
                try:
                    from app.services.notification_service import notification_service
                    from app.integrations.slack import SlackIntegration
                    slack = SlackIntegration()

                    await notification_service.dispatch_agent_alert(
                        startup_id=startup_context.get("id"),
                        agent_name="FinanceCFOAgent",
                        channel="slack",
                        dispatch_func=slack.execute_action,
                        action="send_message",
                        params={
                            "channel": "#revenue",
                            "text": f"📉 *Revenue Anomaly — {startup_context.get('name', 'Startup')}*\n{detail}\nCustomer: {customer_id}",
                        },
                    )
                except Exception:
                    pass

                # Alert CustomerSuccess to prevent further churn
                await self.publish_to_bus(
                    topic="revenue_anomaly",
                    data={"event": event, "customer_id": customer_id, "detail": detail},
                    target_agents=["CustomerSuccessAgent"],
                )

                return f"Revenue anomaly handled: {detail}"

            elif action_type == "invoice_overdue_recovery":
                # Proactive scan: find overdue invoices and draft dunning emails
                try:
                    from app.integrations.stripe import StripeIntegration
                    stripe = StripeIntegration()
                    result = await stripe.execute_action("list_invoices", {"status": "open", "limit": 50})

                    overdue = [i for i in result.get("invoices", []) if i.get("due_date") and i["due_date"] < int(__import__("time").time())]

                    if not overdue:
                        return "No overdue invoices found"

                    # Draft dunning emails for each overdue invoice
                    for inv in overdue[:5]:  # Cap at 5 per run
                        email = inv.get("customer_email")
                        if not email:
                            continue

                        from app.services.notification_service import notification_service
                        from app.integrations.gmail import gmail_integration

                        await notification_service.dispatch_agent_alert(
                            startup_id=startup_context.get("id"),
                            agent_name="FinanceCFOAgent",
                            channel="email",
                            dispatch_func=gmail_integration.execute_action,
                            action="send_email",
                            params={
                                "to": startup_context.get("founder_email", ""),
                                "subject": f"📋 Overdue Invoice: {email} — ${inv['amount_due']:.2f}",
                                "body": f"""
<h3>Overdue Invoice Detected</h3>
<p><strong>Customer:</strong> {email}</p>
<p><strong>Amount Due:</strong> ${inv['amount_due']:.2f}</p>
<p><strong>Invoice:</strong> {inv['id']}</p>
<p><a href="{inv.get('hosted_invoice_url', '#')}">View Invoice in Stripe</a></p>
<hr>
<p>Consider sending a polite reminder to this customer or retrying the charge.</p>
""",
                                "priority": "high",
                                "agent_name": "FinanceCFOAgent",
                                "severity": "warning",
                            },
                        )

                    return f"Processed {len(overdue)} overdue invoices, notified founder"

                except Exception as e:
                    return f"Invoice recovery scan failed: {str(e)}"

            elif action_type == "unit_economics_tracker":
                # Calculate and report unit economics from Stripe data
                try:
                    from app.integrations.stripe import StripeIntegration
                    stripe = StripeIntegration()

                    # Gather data points
                    mrr = await stripe._calculate_mrr()
                    customers = await stripe._get_customer_counts()
                    subs = await stripe._get_subscription_stats()
                    timeline = await stripe.execute_action("get_revenue_timeline", {"months": 6})

                    total_customers = customers.get("total", 0)
                    new_this_month = customers.get("new_this_month", 0)
                    churn_rate = subs.get("churn_rate", 0)
                    mom_growth = timeline.get("mom_growth_pct", 0)

                    # Calculate unit economics
                    arpu = mrr / total_customers if total_customers > 0 else 0
                    ltv = arpu / (churn_rate / 100) if churn_rate > 0 else arpu * 24  # Assume 24 month lifetime if no churn

                    report = {
                        "mrr": mrr,
                        "arr": mrr * 12,
                        "arpu": round(arpu, 2),
                        "ltv": round(ltv, 2),
                        "total_customers": total_customers,
                        "new_this_month": new_this_month,
                        "churn_rate": churn_rate,
                        "mom_growth": mom_growth,
                    }

                    # Notify founder
                    from app.services.notification_service import notification_service
                    from app.integrations.gmail import gmail_integration

                    await notification_service.dispatch_agent_alert(
                        startup_id=startup_context.get("id"),
                        agent_name="FinanceCFOAgent",
                        channel="email",
                        dispatch_func=gmail_integration.execute_action,
                        action="send_email",
                        params={
                            "to": startup_context.get("founder_email", ""),
                            "subject": f"📊 Unit Economics Report — {startup_context.get('name', 'Startup')}",
                            "body": f"""
<h3>Monthly Unit Economics</h3>
<table style="border-collapse:collapse; width:100%;">
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>MRR</strong></td><td style="padding:8px; border:1px solid #ddd;">${mrr:,.2f}</td></tr>
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>ARR</strong></td><td style="padding:8px; border:1px solid #ddd;">${mrr*12:,.2f}</td></tr>
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>ARPU</strong></td><td style="padding:8px; border:1px solid #ddd;">${arpu:,.2f}/mo</td></tr>
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>LTV</strong></td><td style="padding:8px; border:1px solid #ddd;">${ltv:,.2f}</td></tr>
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Customers</strong></td><td style="padding:8px; border:1px solid #ddd;">{total_customers} (+{new_this_month} this month)</td></tr>
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>Churn Rate</strong></td><td style="padding:8px; border:1px solid #ddd;">{churn_rate}%</td></tr>
<tr><td style="padding:8px; border:1px solid #ddd;"><strong>MoM Growth</strong></td><td style="padding:8px; border:1px solid #ddd;">{mom_growth}%</td></tr>
</table>
""",
                            "priority": "normal",
                            "agent_name": "FinanceCFOAgent",
                            "severity": "info",
                        },
                    )

                    return f"Unit economics report generated: MRR=${mrr:,.2f}, LTV=${ltv:,.2f}"

                except Exception as e:
                    return f"Unit economics tracker failed: {str(e)}"

            elif action_type == "investor_update_generator":
                # Auto-draft a monthly investor update email
                try:
                    from app.integrations.stripe import StripeIntegration
                    stripe = StripeIntegration()

                    mrr = await stripe._calculate_mrr()
                    timeline = await stripe.execute_action("get_revenue_timeline", {"months": 3})
                    customers = await stripe._get_customer_counts()
                    subs = await stripe._get_subscription_stats()

                    startup_name = startup_context.get("name", "Our Startup")
                    mom_growth = timeline.get("mom_growth_pct", 0)

                    from app.services.notification_service import notification_service
                    from app.integrations.gmail import gmail_integration

                    await notification_service.dispatch_agent_alert(
                        startup_id=startup_context.get("id"),
                        agent_name="FinanceCFOAgent",
                        channel="email",
                        dispatch_func=gmail_integration.execute_action,
                        action="send_email",
                        params={
                            "to": startup_context.get("founder_email", ""),
                            "subject": f"📝 Monthly Investor Update Draft — {startup_name}",
                            "body": f"""
<h2>Monthly Investor Update — {startup_name}</h2>
<p><em>Auto-drafted by your AI CFO. Review and forward to your investors.</em></p>

<h3>🔑 Key Metrics</h3>
<ul>
<li><strong>MRR:</strong> ${mrr:,.2f} ({'+' if mom_growth >= 0 else ''}{mom_growth}% MoM)</li>
<li><strong>ARR Run Rate:</strong> ${mrr*12:,.2f}</li>
<li><strong>Total Customers:</strong> {customers.get('total', 0)}</li>
<li><strong>New This Month:</strong> {customers.get('new_this_month', 0)}</li>
<li><strong>Churn Rate:</strong> {subs.get('churn_rate', 0)}%</li>
</ul>

<h3>📈 Revenue Trend (Last 3 Months)</h3>
<ul>
{''.join(f'<li>{m["month"]}: ${m["revenue"]:,.2f}</li>' for m in timeline.get("timeline", [])[-3:])}
</ul>

<h3>🎯 Highlights</h3>
<p><em>[Add your wins, product updates, and asks here]</em></p>

<h3>🚨 Challenges</h3>
<p><em>[Add any blockers or areas where you need help]</em></p>

<h3>💡 Asks</h3>
<p><em>[Introductions, advice, or resources needed]</em></p>
""",
                            "priority": "normal",
                            "agent_name": "FinanceCFOAgent",
                            "severity": "info",
                        },
                    )

                    return f"Investor update draft generated for {startup_name} (MRR: ${mrr:,.2f})"

                except Exception as e:
                    return f"Investor update generation failed: {str(e)}"
            
            else:
                return await super().autonomous_action(action, startup_context)
                
        except Exception as e:
            logger.error("FinanceCFO autonomous action failed", action=action_type, error=str(e))
            return f"Action failed: {str(e)}"


# Singleton instance
finance_cfo_agent = FinanceCFOAgent()
