"""
WebSocket Connection Manager
Handles real-time broadcasting of agent activities to frontend dashboards.
"""

from typing import Dict, List, Any
import structlog
from fastapi import WebSocket

logger = structlog.get_logger()

class ConnectionManager:
    def __init__(self):
        # Maps startup_id to a list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, startup_id: str):
        """Accept a connection and add it to the startup's broadcast group."""
        await websocket.accept()
        if startup_id not in self.active_connections:
            self.active_connections[startup_id] = []
        self.active_connections[startup_id].append(websocket)
        logger.info("WebSocket connected", startup_id=startup_id, total_clients=len(self.active_connections[startup_id]))

    def disconnect(self, websocket: WebSocket, startup_id: str):
        """Remove a connection on disconnect."""
        if startup_id in self.active_connections:
            if websocket in self.active_connections[startup_id]:
                self.active_connections[startup_id].remove(websocket)
            if not self.active_connections[startup_id]:
                del self.active_connections[startup_id]
        logger.info("WebSocket disconnected", startup_id=startup_id)
        
    async def broadcast_to_startup(self, startup_id: str, message: Dict[str, Any]):
        """
        Send a JSON payload to all connected clients for a specific startup.
        Used for streaming live agent activity to the UI.
        """
        if startup_id in self.active_connections:
            dead_sockets = []
            for connection in self.active_connections[startup_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning("Failed to broadast to websocket", error=str(e))
                    dead_sockets.append(connection)
            
            # Clean up dead connections
            for dead in dead_sockets:
                self.disconnect(dead, startup_id)


# Global singleton manager
websocket_manager = ConnectionManager()
