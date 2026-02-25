from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.openclaw_service import run_openclaw_session
import structlog
import asyncio

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.websocket("/stream")
async def openclaw_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        # Parse the JSON or string
        directive = data

        # Ensure we run the OpenClaw session and route output over WebSocket
        await run_openclaw_session(websocket, directive)

    except WebSocketDisconnect:
        logger.info("OpenClaw WebSocket disconnected")
    except Exception as e:
        logger.error(f"OpenClaw WebSocket Error: {e}")
        try:
            await websocket.send_text(f'{{"type": "log", "action": "ERROR", "details": "Disconnected unexpectedly"}}')
        except:
            pass
        finally:
            await websocket.close()
