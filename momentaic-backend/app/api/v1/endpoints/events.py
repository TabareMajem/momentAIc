
"""
Events Endpoint
Real-time activity stream for dashboard
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio

from app.core.security import get_current_active_user, get_superuser
from app.models.user import User
from app.core.events import subscribe_events

router = APIRouter()

@router.get("/activity-stream")
async def activity_stream(
    current_user: User = Depends(get_current_active_user),
):
    """
    Stream real-time activity events (SSE).
    
    Returns:
        Server-Sent Events stream of application activities.
    """
    
    async def event_generator():
        # Initial connection message
        yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
        
        # Subscribe to global events channel
        # In a real multi-tenant app, we might filter by tenant ID here
        async for message in subscribe_events(channel="momentaic:events"):
            yield f"data: {message}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no", # Nginx buffering disable
        }
    )

@router.post("/test-event", include_in_schema=False)
async def trigger_test_event(
    event_type: str = "test",
    message: str = "Hello World",
    current_user: User = Depends(get_superuser),
):
    """Trigger a test event (Superuser only)"""
    from app.core.events import publish_event
    import datetime
    
    await publish_event(
        event_type=event_type,
        data={
            "message": message,
            "user": current_user.email,
            "timestamp": str(datetime.datetime.utcnow())
        }
    )
    return {"status": "Event published"}
