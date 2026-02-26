"""
DAG Execution API Endpoint
Receives a visual agent DAG from the frontend AgentComposability canvas
and executes it through the ChainExecutor.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import structlog

from app.agents.chain_executor import ChainExecutor, ChainStep
from app.agents.registry import agent_registry

logger = structlog.get_logger()

router = APIRouter()


class DAGNode(BaseModel):
    id: str
    agent_type: str


class DAGEdge(BaseModel):
    source: str
    target: str


class DAGExecutionRequest(BaseModel):
    nodes: List[DAGNode]
    edges: List[DAGEdge]
    initial_input: str = Field(default="Analyze and create a growth strategy.")


class DAGExecutionResponse(BaseModel):
    chain_id: str
    status: str
    steps: List[Dict[str, Any]]
    final_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/execute-dag", response_model=DAGExecutionResponse)
async def execute_agent_dag(startup_id: str, request: DAGExecutionRequest):
    """
    Execute a visual agent DAG from the AgentComposability canvas.
    
    1. Receives nodes (agents) and edges (connections) from React Flow
    2. Topologically sorts them
    3. Runs each agent in sequence, passing output from one to the next
    """
    if not request.nodes:
        raise HTTPException(status_code=400, detail="DAG must have at least one node")

    logger.info("dag_execution_start",
                startup_id=startup_id,
                node_count=len(request.nodes),
                edge_count=len(request.edges))

    try:
        # Topological sort based on edges
        sorted_agents = _topological_sort(request.nodes, request.edges)

        executor = ChainExecutor()

        # Build chain steps
        steps = []
        for order, node in enumerate(sorted_agents):
            step = ChainStep(
                agent_id=node.agent_type,
                order=order,
                input_context={"initial_input": request.initial_input} if order == 0 else {}
            )
            steps.append(step)

        # Execute the chain
        result = await executor.execute(
            steps=steps,
            initial_context={
                "startup_id": startup_id,
                "goal": request.initial_input,
            }
        )

        return DAGExecutionResponse(
            chain_id=result.chain_id,
            status=result.status.value,
            steps=[s.to_dict() for s in result.steps],
            final_output=result.final_output,
            error=result.error
        )

    except Exception as e:
        logger.error("dag_execution_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"DAG execution failed: {str(e)}")


def _topological_sort(nodes: List[DAGNode], edges: List[DAGEdge]) -> List[DAGNode]:
    """Simple topological sort for the DAG nodes."""
    node_map = {n.id: n for n in nodes}
    in_degree = {n.id: 0 for n in nodes}
    adjacency = {n.id: [] for n in nodes}

    for edge in edges:
        if edge.target in in_degree:
            in_degree[edge.target] += 1
        if edge.source in adjacency:
            adjacency[edge.source].append(edge.target)

    # Kahn's algorithm
    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    sorted_ids = []

    while queue:
        current = queue.pop(0)
        sorted_ids.append(current)
        for neighbor in adjacency.get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Return nodes in topological order
    return [node_map[nid] for nid in sorted_ids if nid in node_map]
