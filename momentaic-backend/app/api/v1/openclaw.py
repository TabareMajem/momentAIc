from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.openclaw_service import run_openclaw_session
import structlog
import asyncio
import json

logger = structlog.get_logger(__name__)
router = APIRouter()

class OpenClawRequest(BaseModel):
    directive: str

class SSEWebsocketShim:
    """A fake WebSocket that captures send_text calls to a queue for SSE streaming."""
    def __init__(self):
         self.queue = asyncio.Queue()
    async def send_text(self, data: str):
         await self.queue.put(data)

async def sse_generator(directive: str):
    shim = SSEWebsocketShim()
    
    # Run the session in the background
    task = asyncio.create_task(run_openclaw_session(shim, directive))
    
    while True:
        try:
            # Wait for data or task completion
            data = await asyncio.wait_for(shim.queue.get(), timeout=1.0)
            yield f"data: {data}\n\n"
        except asyncio.TimeoutError:
            if task.done():
                break
            continue
            
    # Yield any remaining items in queue
    while not shim.queue.empty():
        data = shim.queue.get_nowait()
        yield f"data: {data}\n\n"

@router.post("/stream")
async def openclaw_stream(request: OpenClawRequest):
    """
    Execute OpenClaw session and stream updates via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        sse_generator(request.directive),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.get("/stream")
async def openclaw_stream_get(directive: str):
    """
    Execute OpenClaw session and stream updates via Server-Sent Events (SSE) using GET parameters.
    """
    return StreamingResponse(
        sse_generator(directive),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
