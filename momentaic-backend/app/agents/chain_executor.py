"""
Chain Executor - Multi-Agent Workflow Orchestration
Executes chains of agents with data handoffs and intelligent error handling
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4
import structlog
import asyncio

logger = structlog.get_logger()


class ChainStatus(str, Enum):
    """Chain execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some steps succeeded


class StepStatus(str, Enum):
    """Individual step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChainStep:
    """A single step in an agent chain"""
    agent_id: str
    order: int
    status: StepStatus = StepStatus.PENDING
    input_context: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "order": self.order,
            "status": self.status.value,
            "input_context": self.input_context,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds
        }


@dataclass
class ChainResult:
    """Result of a chain execution"""
    chain_id: str
    status: ChainStatus
    steps: List[ChainStep]
    final_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_seconds: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "final_output": self.final_output,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_duration_seconds": self.total_duration_seconds
        }


class AgentChainExecutor:
    """
    Executes chains of agents with data handoffs
    
    Features:
    - Sequential agent execution
    - Context accumulation across steps
    - Intelligent error handling and retry
    - Parallel execution support (future)
    """
    
    def __init__(self):
        self._running_chains: Dict[str, ChainResult] = {}
        self._agent_registry: Dict[str, Any] = {}
        logger.info("Chain Executor initialized")
    
    def _get_agent(self, agent_id: str):
        """Lazy-load agent by ID"""
        # Map agent IDs to actual agent instances
        agent_map = {
            "supervisor": lambda: __import__('app.agents.supervisor', fromlist=['supervisor_agent']).supervisor_agent,
            "sales": lambda: __import__('app.agents.sales_agent', fromlist=['sales_agent']).sales_agent,
            "content": lambda: __import__('app.agents.content_agent', fromlist=['content_agent']).content_agent,
            "tech_lead": lambda: __import__('app.agents.tech_lead_agent', fromlist=['tech_lead_agent']).tech_lead_agent,
            "finance_cfo": lambda: __import__('app.agents.finance_cfo_agent', fromlist=['finance_cfo_agent']).finance_cfo_agent,
            "legal_counsel": lambda: __import__('app.agents.legal_counsel_agent', fromlist=['legal_counsel_agent']).legal_counsel_agent,
            "growth_hacker": lambda: __import__('app.agents.growth_hacker_agent', fromlist=['growth_hacker_agent']).growth_hacker_agent,
            "product_pm": lambda: __import__('app.agents.product_pm_agent', fromlist=['product_pm_agent']).product_pm_agent,
            "customer_success": lambda: __import__('app.agents.customer_success_agent', fromlist=['customer_success_agent']).customer_success_agent,
            "data_analyst": lambda: __import__('app.agents.data_analyst_agent', fromlist=['data_analyst_agent']).data_analyst_agent,
            "hr_operations": lambda: __import__('app.agents.hr_operations_agent', fromlist=['hr_operations_agent']).hr_operations_agent,
            "marketing": lambda: __import__('app.agents.marketing_agent', fromlist=['marketing_agent']).marketing_agent,
            "community": lambda: __import__('app.agents.community_agent', fromlist=['community_agent']).community_agent,
            "devops": lambda: __import__('app.agents.devops_agent', fromlist=['devops_agent']).devops_agent,
            "strategy": lambda: __import__('app.agents.strategy_agent', fromlist=['strategy_agent']).strategy_agent,
            "browser": lambda: __import__('app.agents.browser_agent', fromlist=['browser_agent']).browser_agent,
            "design": lambda: __import__('app.agents.design_agent', fromlist=['design_agent']).design_agent,
            "lead_scraper": lambda: __import__('app.agents.lead_scraper_agent', fromlist=['lead_scraper_agent']).lead_scraper_agent,
            "lead_researcher": lambda: __import__('app.agents.lead_researcher_agent', fromlist=['lead_researcher_agent']).lead_researcher_agent,
            "sdr": lambda: __import__('app.agents.sdr_agent', fromlist=['sdr_agent']).sdr_agent,
            "judgement": lambda: __import__('app.agents.judgement_agent', fromlist=['judgement_agent']).judgement_agent,
            "qa_tester": lambda: __import__('app.agents.qa_tester_agent', fromlist=['qa_tester_agent']).qa_tester_agent,
            "launch_strategist": lambda: __import__('app.agents.launch_strategist_agent', fromlist=['launch_strategist_agent']).launch_strategist_agent,
            "launch_executor": lambda: __import__('app.agents.launch_executor_agent', fromlist=['launch_executor_agent']).launch_executor_agent,
            "onboarding_coach": lambda: __import__('app.agents.onboarding_coach_agent', fromlist=['onboarding_coach_agent']).onboarding_coach_agent,
            "competitor_intel": lambda: __import__('app.agents.competitor_intel_agent', fromlist=['competitor_intel_agent']).competitor_intel_agent,
            "fundraising_coach": lambda: __import__('app.agents.fundraising_coach_agent', fromlist=['fundraising_coach_agent']).fundraising_coach_agent,
            "ambassador_outreach": lambda: __import__('app.agents.ambassador_outreach_agent', fromlist=['ambassador_outreach_agent']).ambassador_outreach_agent,
        }
        
        if agent_id not in self._agent_registry:
            if agent_id in agent_map:
                self._agent_registry[agent_id] = agent_map[agent_id]()
            else:
                logger.warning(f"Unknown agent: {agent_id}")
                return None
        
        return self._agent_registry.get(agent_id)
    
    async def execute_chain(
        self,
        agent_chain: List[str],
        initial_context: Dict[str, Any],
        stop_on_error: bool = True,
        timeout_per_step: float = 300.0,  # 5 minutes per step
    ) -> Dict[str, Any]:
        """
        Execute a chain of agents in sequence
        
        Each agent receives the accumulated context from previous steps.
        """
        chain_id = str(uuid4())
        started_at = datetime.utcnow()
        
        # Initialize steps
        steps = [
            ChainStep(agent_id=agent_id, order=i)
            for i, agent_id in enumerate(agent_chain)
        ]
        
        result = ChainResult(
            chain_id=chain_id,
            status=ChainStatus.RUNNING,
            steps=steps,
            started_at=started_at
        )
        self._running_chains[chain_id] = result
        
        logger.info(
            "Chain execution started",
            chain_id=chain_id,
            agents=agent_chain,
            context_keys=list(initial_context.keys())
        )
        
        # Accumulated context passed between agents
        accumulated_context = dict(initial_context)
        last_successful_output = None
        
        for step in steps:
            step.started_at = datetime.utcnow()
            step.status = StepStatus.RUNNING
            step.input_context = dict(accumulated_context)
            
            agent = self._get_agent(step.agent_id)
            if not agent:
                step.status = StepStatus.FAILED
                step.error = f"Agent not found: {step.agent_id}"
                step.completed_at = datetime.utcnow()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
                
                if stop_on_error:
                    result.status = ChainStatus.FAILED
                    result.error = step.error
                    break
                continue
            
            try:
                # Execute agent
                output = await self._execute_agent(
                    agent=agent,
                    agent_id=step.agent_id,
                    context=accumulated_context,
                    timeout=timeout_per_step
                )
                
                step.status = StepStatus.COMPLETED
                step.output = output
                step.completed_at = datetime.utcnow()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
                
                # Accumulate output into context for next step
                if isinstance(output, dict):
                    accumulated_context.update(output)
                    last_successful_output = output
                else:
                    accumulated_context[f"{step.agent_id}_output"] = output
                    last_successful_output = {f"{step.agent_id}_output": output}
                
                logger.info(
                    "Chain step completed",
                    chain_id=chain_id,
                    agent=step.agent_id,
                    duration=step.duration_seconds
                )
                
            except asyncio.TimeoutError:
                step.status = StepStatus.FAILED
                step.error = f"Timeout after {timeout_per_step}s"
                step.completed_at = datetime.utcnow()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
                
                if stop_on_error:
                    result.status = ChainStatus.FAILED
                    result.error = step.error
                    break
                    
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                step.completed_at = datetime.utcnow()
                step.duration_seconds = (step.completed_at - step.started_at).total_seconds()
                
                logger.error(
                    "Chain step failed",
                    chain_id=chain_id,
                    agent=step.agent_id,
                    error=str(e)
                )
                
                if stop_on_error:
                    result.status = ChainStatus.FAILED
                    result.error = step.error
                    break
        
        # Determine final status
        result.completed_at = datetime.utcnow()
        result.total_duration_seconds = (result.completed_at - result.started_at).total_seconds()
        
        completed_count = len([s for s in steps if s.status == StepStatus.COMPLETED])
        failed_count = len([s for s in steps if s.status == StepStatus.FAILED])
        
        if failed_count == 0:
            result.status = ChainStatus.COMPLETED
            result.final_output = last_successful_output
        elif completed_count > 0:
            result.status = ChainStatus.PARTIAL
            result.final_output = last_successful_output
        else:
            result.status = ChainStatus.FAILED
        
        logger.info(
            "Chain execution finished",
            chain_id=chain_id,
            status=result.status.value,
            completed=completed_count,
            failed=failed_count,
            duration=result.total_duration_seconds
        )
        
        return result.to_dict()
    
    async def _execute_agent(
        self,
        agent: Any,
        agent_id: str,
        context: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """Execute a single agent with timeout"""
        
        # Build the message/request for the agent
        task_name = context.get('task_name', '')
        task_description = context.get('task_description', '')
        startup_context = {
            k: v for k, v in context.items() 
            if k not in ['task_name', 'task_description']
        }
        
        message = f"{task_name}: {task_description}" if task_name else str(context.get('message', 'Execute task'))
        
        # Different agents have different methods
        if hasattr(agent, 'process'):
            # Most agents have a process method
            result = await asyncio.wait_for(
                agent.process(
                    message=message,
                    startup_context=startup_context,
                    user_id=context.get('user_id', 'system')
                ),
                timeout=timeout
            )
        elif hasattr(agent, 'generate'):
            # Content-type agents
            result = await asyncio.wait_for(
                agent.generate(
                    platform=context.get('platform', 'linkedin'),
                    topic=message,
                    startup_context=startup_context,
                    content_type=context.get('content_type', 'post')
                ),
                timeout=timeout
            )
        elif hasattr(agent, 'analyze'):
            # Analysis-type agents
            result = await asyncio.wait_for(
                agent.analyze(context=startup_context),
                timeout=timeout
            )
        elif hasattr(agent, 'execute'):
            # Execution-type agents
            result = await asyncio.wait_for(
                agent.execute(context=startup_context),
                timeout=timeout
            )
        elif hasattr(agent, 'route'):
            # Supervisor/router agents
            result = await asyncio.wait_for(
                agent.route(
                    message=message,
                    startup_context=startup_context,
                    user_id=context.get('user_id', 'system'),
                    startup_id=context.get('startup_id', '')
                ),
                timeout=timeout
            )
        else:
            # Fallback - try to call it directly
            logger.warning(f"Agent {agent_id} has no standard method, attempting direct call")
            result = {"warning": f"Agent {agent_id} method not found", "agent": agent_id}
        
        # Normalize result
        if isinstance(result, str):
            return {"response": result, "agent": agent_id}
        elif isinstance(result, dict):
            result["agent"] = agent_id
            return result
        else:
            return {"output": str(result), "agent": agent_id}
    
    async def execute_parallel(
        self,
        agent_chains: List[List[str]],
        initial_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute multiple chains in parallel"""
        tasks = [
            self.execute_chain(chain, initial_context)
            for chain in agent_chains
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            r if isinstance(r, dict) else {"error": str(r)}
            for r in results
        ]
        
    async def execute_dag(
        self,
        dag: Dict[str, Dict[str, Any]],
        initial_context: Dict[str, Any],
        stop_on_error: bool = True,
        timeout_per_step: float = 300.0,
    ) -> Dict[str, Any]:
        """
        Execute a Directed Acyclic Graph (DAG) of agents.
        Allows passing outputs of Agent A directly to Agent B autonomously.
        
        DAG Format:
        {
            "step_id_1": {
                "agent": "researcher",
                "depends_on": []
            },
            "step_id_2": {
                "agent": "writer",
                "depends_on": ["step_id_1"]
            }
        }
        """
        chain_id = str(uuid4())
        started_at = datetime.utcnow()
        logger.info(f"DAG execution started {chain_id}")
        
        # State tracking
        node_outputs: Dict[str, Any] = {}
        node_tasks: Dict[str, asyncio.Task] = {}
        events: Dict[str, asyncio.Event] = {node: asyncio.Event() for node in dag.keys()}
        
        async def run_node(node_id: str, node_config: Dict[str, Any]):
            # Wait for dependencies
            depends_on = node_config.get("depends_on", [])
            for dep in depends_on:
                if dep in events:
                    await events[dep].wait()
                    # If dependency failed and stop_on_error is True, cascade failure
                    if stop_on_error and isinstance(node_outputs.get(dep), Exception):
                        raise Exception(f"Dependency {dep} failed")
            
            # Build accumulated context from dependencies
            accumulated_context = dict(initial_context)
            for dep in depends_on:
                if dep in node_outputs and isinstance(node_outputs[dep], dict):
                    # Output of Agent A directly injected into Agent B's context payload
                    accumulated_context[f"{dep}_output"] = node_outputs[dep]
                    # Also merge flat for seamless extraction
                    accumulated_context.update(node_outputs[dep])
            
            agent_id = node_config["agent"]
            agent = self._get_agent(agent_id)
            if not agent:
                raise ValueError(f"Agent not found: {agent_id}")
                
            # Execute
            try:
                output = await self._execute_agent(
                    agent=agent,
                    agent_id=agent_id,
                    context=accumulated_context,
                    timeout=timeout_per_step
                )
                node_outputs[node_id] = output
                return output
            except Exception as e:
                node_outputs[node_id] = e
                logger.error(f"DAG Node {node_id} failed", error=str(e))
                if stop_on_error:
                    raise e
                return {"error": str(e)}
            finally:
                events[node_id].set()

        # Fire off all node tasks concurrently; they will wait on their respective events
        for node_id, config in dag.items():
            node_tasks[node_id] = asyncio.create_task(run_node(node_id, config))
            
        # Wait for all the graph nodes to finish
        results = await asyncio.gather(*node_tasks.values(), return_exceptions=not stop_on_error)
        
        completed_at = datetime.utcnow()
        duration = (completed_at - started_at).total_seconds()
        
        # Formulate final output payload
        final_status = ChainStatus.COMPLETED
        for r in results:
            if isinstance(r, Exception):
                final_status = ChainStatus.FAILED
                
        logger.info(f"DAG execution finished {chain_id}", status=final_status.value, duration=duration)
        
        return {
            "chain_id": chain_id,
            "status": final_status.value,
            "final_outputs": {k: (str(v) if isinstance(v, Exception) else v) for k, v in node_outputs.items()},
            "duration_seconds": duration,
            "platform": "momentaic_dag",
        }
    
    def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a running chain"""
        if chain_id in self._running_chains:
            return self._running_chains[chain_id].to_dict()
        return None
    
    def cancel_chain(self, chain_id: str) -> bool:
        """Cancel a running chain (best effort)"""
        if chain_id in self._running_chains:
            self._running_chains[chain_id].status = ChainStatus.FAILED
            self._running_chains[chain_id].error = "Cancelled by user"
            return True
        return False


# Singleton instance
chain_executor = AgentChainExecutor()
