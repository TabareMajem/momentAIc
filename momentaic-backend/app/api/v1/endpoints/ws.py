"""
WebSocket Endpoints
Handles real-time streaming to frontend clients (e.g., Live Agent Dashboard)
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog
from app.core.websocket import websocket_manager

router = APIRouter()
logger = structlog.get_logger()

@router.websocket("/agents/{startup_id}")
async def websocket_agents_endpoint(websocket: WebSocket, startup_id: str):
    """
    WebSocket for the Real-Time Agent Dashboard.
    Streams live activity events for a specific startup.
    """
    await websocket_manager.connect(websocket, startup_id)
    try:
        while True:
            # Keep connection alive. We don't expect client-to-server WS messages here,
            # but we need to await receive to know if the client disconnects.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, startup_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        websocket_manager.disconnect(websocket, startup_id)
