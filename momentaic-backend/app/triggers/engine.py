"""
Trigger Engine
Evaluates trigger rules and activates agents proactively
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import structlog
from croniter import croniter

from app.models.trigger import TriggerRule, TriggerLog, TriggerType, TriggerLogStatus
from app.models.integration import IntegrationData

logger = structlog.get_logger()


class TriggerEngine:
    """
    Proactive trigger evaluation engine
    
    Evaluates trigger rules against data and activates agents
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def evaluate_startup_triggers(
        self,
        startup_id: str,
        data_context: Dict[str, Any] = None,
    ) -> List[TriggerLog]:
        """
        Evaluate all active triggers for a startup
        
        Called periodically or when new data arrives
        """
        # Get active triggers
        result = await self.db.execute(
            select(TriggerRule).where(
                and_(
                    TriggerRule.startup_id == startup_id,
                    TriggerRule.is_active == True,
                    TriggerRule.is_paused == False,
                )
            )
        )
        rules = result.scalars().all()
        
        triggered_logs = []
        
        for rule in rules:
            should_trigger = await self._evaluate_rule(rule, data_context)
            
            if should_trigger:
                # Check rate limits
                if not await self._check_rate_limit(rule):
                    logger.info("Trigger rate limited", rule_id=str(rule.id))
                    continue
                
                # Create trigger log
                trigger_log = await self._create_trigger_log(rule, data_context)
                triggered_logs.append(trigger_log)
                
                # Execute action
                await self._execute_action(rule, trigger_log, data_context)
        
        return triggered_logs
    
    async def _evaluate_rule(
        self,
        rule: TriggerRule,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate if a rule should trigger"""
        
        if rule.trigger_type == TriggerType.METRIC:
            return await self._evaluate_metric_trigger(rule, context)
        
        elif rule.trigger_type == TriggerType.TIME:
            return await self._evaluate_time_trigger(rule)
        
        elif rule.trigger_type == TriggerType.EVENT:
            return await self._evaluate_event_trigger(rule, context)
        
        elif rule.trigger_type == TriggerType.WEBHOOK:
            # Webhooks are evaluated externally
            return False
        
        return False
    
    async def _evaluate_metric_trigger(
        self,
        rule: TriggerRule,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate metric-based trigger"""
        condition = rule.condition
        metric_name = condition.get("metric")
        operator = condition.get("operator")
        threshold = condition.get("value", 0)
        unit = condition.get("unit", "absolute")  # absolute or percent
        
        # Get current and previous metric values
        current_value = context.get(metric_name, 0) if context else 0
        previous_value = await self._get_previous_metric_value(
            rule.startup_id, metric_name
        )
        
        if previous_value is None:
            return False
        
        # Calculate change
        if unit == "percent" and previous_value > 0:
            change = ((current_value - previous_value) / previous_value) * 100
        else:
            change = current_value - previous_value
        
        # Evaluate condition
        if operator == "gt":
            return current_value > threshold
        elif operator == "lt":
            return current_value < threshold
        elif operator == "eq":
            return current_value == threshold
        elif operator == "increases_by":
            return change >= threshold
        elif operator == "decreases_by":
            return change <= -threshold
        elif operator == "changes_by":
            return abs(change) >= threshold
        
        return False
    
    async def _evaluate_time_trigger(self, rule: TriggerRule) -> bool:
        """Evaluate time-based trigger (cron)"""
        condition = rule.condition
        cron_expr = condition.get("cron")
        
        if not cron_expr:
            return False
        
        # Check if it's time to trigger
        last_triggered = rule.last_triggered_at or datetime.min
        cron = croniter(cron_expr, last_triggered)
        next_run = cron.get_next(datetime)
        
        return datetime.utcnow() >= next_run
    
    async def _evaluate_event_trigger(
        self,
        rule: TriggerRule,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate event-based trigger"""
        condition = rule.condition
        event_type = condition.get("event")
        filters = condition.get("filter", {})
        
        # Check if matching event occurred
        triggered_event = context.get("event") if context else None
        
        if triggered_event != event_type:
            return False
        
        # Apply filters
        event_data = context.get("event_data", {})
        for key, filter_condition in filters.items():
            value = event_data.get(key)
            if isinstance(filter_condition, dict):
                # Complex filter like {"gt": 80}
                if "gt" in filter_condition and value <= filter_condition["gt"]:
                    return False
                if "lt" in filter_condition and value >= filter_condition["lt"]:
                    return False
            elif value != filter_condition:
                return False
        
        return True
    
    async def _check_rate_limit(self, rule: TriggerRule) -> bool:
        """Check if trigger is within rate limits"""
        if not rule.last_triggered_at:
            return True
        
        # Check cooldown
        cooldown = timedelta(minutes=rule.cooldown_minutes)
        if datetime.utcnow() - rule.last_triggered_at < cooldown:
            return False
        
        # Check daily limit
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        result = await self.db.execute(
            select(TriggerLog).where(
                and_(
                    TriggerLog.rule_id == rule.id,
                    TriggerLog.triggered_at >= today_start,
                )
            )
        )
        today_count = len(result.scalars().all())
        
        return today_count < rule.max_triggers_per_day
    
    async def _create_trigger_log(
        self,
        rule: TriggerRule,
        context: Dict[str, Any],
    ) -> TriggerLog:
        """Create a trigger log entry"""
        action = rule.action
        requires_approval = action.get("requires_approval", False)
        
        log = TriggerLog(
            rule_id=rule.id,
            startup_id=rule.startup_id,
            status=TriggerLogStatus.TRIGGERED,
            trigger_context=context or {},
            requires_approval=requires_approval,
        )
        
        self.db.add(log)
        
        # Update rule
        rule.last_triggered_at = datetime.utcnow()
        rule.trigger_count += 1
        
        await self.db.flush()
        
        return log
    
    async def _execute_action(
        self,
        rule: TriggerRule,
        log: TriggerLog,
        context: Dict[str, Any],
    ):
        """Execute the trigger action"""
        action = rule.action
        
        if action.get("requires_approval"):
            log.status = TriggerLogStatus.AWAITING_APPROVAL
            await self.db.flush()
            logger.info("Trigger awaiting approval", rule_id=str(rule.id))
            return
        
        log.status = TriggerLogStatus.EXECUTING
        await self.db.flush()
        
        try:
            # Get agent and execute task
            agent_type = action.get("agent")
            task = action.get("task")
            
            result = None
            
            # 1. Check for Ecosystem Agents
            if agent_type in ["sniper", "sniper_agent"]:
                from app.services.ecosystem_service import ecosystem_service
                result = await ecosystem_service.find_leads({"query": task})
                
            elif agent_type in ["viral", "viral_agent"]:
                from app.services.ecosystem_service import ecosystem_service
                result = await ecosystem_service.generate_viral_content(task)
                
            elif agent_type in ["content", "content_creator"]:
                 # Could be internal or external
                 from app.services.ecosystem_service import ecosystem_service
                 result = await ecosystem_service.create_content_strategy(task)
                 
            # 2. Check for AgentForge Agents
            elif agent_type in ["orchestrator", "orchestrator_agent"]:
                from app.services.ecosystem_service import ecosystem_service
                result = await ecosystem_service.orchestrate_tasks(task)
                
            elif agent_type in ["research", "research_agent"]:
                from app.services.ecosystem_service import ecosystem_service
                result = await ecosystem_service.deep_research(task)
                
            elif agent_type in ["voice", "voice_agent"]:
                from app.services.ecosystem_service import ecosystem_service
                result = await ecosystem_service.synthesize_voice(text=task, action="tts")
                
            elif agent_type in ["developer", "dev_agent"]:
                from app.services.ecosystem_service import ecosystem_service
                result = await ecosystem_service.execute_dev_task(tool="generic", args={"task": task})
                
            # 3. Internal Agents (Fallback or specific)
            elif agent_type:
                 # In production, route via Swarm Router or direct Agent call
                # [PHASE 25 FIX] Real execution logic
                from app.agents.swarm_router import SwarmRouter
                router = SwarmRouter()
                
                action_type = action.get("type") # e.g., "agent_task", "notification"
                action_data = action.get("data", {})
                context_data = context or {}
                
                # If it's an agent task, route it
                if action_type == "agent_task":
                    task_prompt = action_data.get("prompt", "")
                    # Execute via swarm
                    response = await router.route_task(
                        task=task_prompt,
                        context={"startup_id": str(rule.startup_id), "trigger_context": context_data}
                    )
                    log.agent_response = response
                    # Set result to indicate an action was taken, for the 'if result:' block
                    result = {"success": response.get("success", True), "source": "swarm_router"}
                elif action_type == "notification":
                    # Send notification
                    from app.tasks.tasks import send_email
                    user_email = context_data.get("user_email")
                    if user_email:
                        send_email(
                            to_email=user_email,
                            subject=f"Trigger Alert: {rule.name}",
                            body=action_data.get("message", "Trigger fired")
                        )
                    log.agent_response = {"status": "sent", "type": "notification"}
                    result = {"success": True, "source": "notification"}
                else:
                    log.agent_response = {"result": "Unknown action type", "mock": False, "success": False, "source": "internal", "message": "Unknown action type"}
                    result = None # No specific agent result to process further
            
            if result:
                log.agent_response = {
                    "agent": agent_type,
                    "task": task,
                    "result": result
                }
                log.status = TriggerLogStatus.COMPLETED if result.get("success", True) else TriggerLogStatus.FAILED
            else:
                log.status = TriggerLogStatus.COMPLETED
                log.agent_response = {"result": "No action taken / Mock success"}
                
            log.completed_at = datetime.utcnow()
            
        except Exception as e:
            log.status = TriggerLogStatus.FAILED
            log.error = str(e)
            logger.error("Trigger execution failed", error=str(e))
        
        await self.db.flush()
    
    async def _get_previous_metric_value(
        self,
        startup_id: str,
        metric_name: str,
    ) -> Optional[float]:
        """Get previous metric value from integration data"""
        result = await self.db.execute(
            select(IntegrationData)
            .where(
                and_(
                    IntegrationData.startup_id == startup_id,
                    IntegrationData.data_type == metric_name,
                )
            )
            .order_by(IntegrationData.synced_at.desc())
            .limit(2)
        )
        records = result.scalars().all()
        
        if len(records) >= 2:
            return records[1].metric_value
        
        return None


# Convenience function
async def evaluate_triggers(
    db: AsyncSession,
    startup_id: str,
    context: Dict[str, Any] = None,
) -> List[TriggerLog]:
    """Evaluate triggers for a startup"""
    engine = TriggerEngine(db)
    return await engine.evaluate_startup_triggers(startup_id, context)
