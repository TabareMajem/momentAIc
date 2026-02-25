import structlog
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.telecom import ProvisionedNumber, TelecomProvider
from app.services.twilio_service import twilio_service
from app.services.voice_webhook_manager import voice_webhook_manager

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.websocket("/stream")
async def voice_stream(websocket: WebSocket):
    """WebSocket endpoint for the CallCenter UI to listen to live transcripts."""
    await voice_webhook_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        voice_webhook_manager.disconnect(websocket)
        logger.info("CallCenter UI disconnected.")

@router.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """
    Webhook endpoint to receive events from Vapi.ai or Retell.
    Broadcasts transcripts to connected Call Center UI clients.
    """
    try:
        payload = await request.json()
        
        # Example Vapi message parsing
        message_type = payload.get("message", {}).get("type")
        if message_type == "transcript":
            text = payload["message"].get("transcript", "")
            role = payload["message"].get("role", "customer") # 'bot' or 'user'
            
            # Broadcast to UI
            await voice_webhook_manager.broadcast({
                "type": "transcript",
                "role": role,
                "text": text,
                "call_id": payload.get("message", {}).get("call", {}).get("id", "sim-call-1")
            })
            
        elif message_type == "status-update":
            status = payload["message"].get("status")
            await voice_webhook_manager.broadcast({
                "type": "status",
                "status": status,
                "call_id": payload.get("message", {}).get("call", {}).get("id", "sim-call-1")
            })

        return {"status": "ok"}
    except Exception as e:
        logger.error("Voice Webhook Error", error=str(e))
        return {"status": "error"}

@router.post("/twilio-incoming")
async def twilio_incoming(request: Request):
    """
    Twilio posts here when a human dials the provisioned Twilio Number.
    We return TwiML XML to direct Twilio to open a WebSocket media stream.
    """
    form_data = await request.form()
    called_number = form_data.get("To")
    caller_number = form_data.get("From")
    call_sid = form_data.get("CallSid")

    logger.info("Incoming Twilio Call", called=called_number, caller=caller_number, sid=call_sid)

    response = VoiceResponse()
    # 1. Answer and perhaps say a greeting
    response.say("Connected to MomentAIc Artificial Intelligence. Initializing cognitive agent.")
    
    # 2. Connect the media stream to our WebSocket Route
    connect = Connect()
    # Note: Replace with actual wss:// domain in production
    stream = Stream(url=f"wss://{request.url.hostname}/api/v1/voice/webhooks/twilio-media-stream")
    stream.parameter(name="call_sid", value=call_sid)
    connect.append(stream)
    response.append(connect)

    return HTMLResponse(content=str(response), media_type="text/xml")

@router.websocket("/twilio-media-stream")
async def twilio_media_stream(websocket: WebSocket):
    """
    Receives raw PCMU Base64 audio frames from Twilio, 
    would route to STT/LLM pipeline in a full production system.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data["event"] == "start":
                logger.info("Twilio media stream started", stream_sid=data["start"]["streamSid"])
            elif data["event"] == "media":
                # Currently dropping media to /dev/null for the UI simulation
                # In production, send to Deepgram WS
                pass
            elif data["event"] == "stop":
                logger.info("Twilio media stream stopped")
                break
    except WebSocketDisconnect:
        logger.info("Twilio Media Stream Disconnected")


# --- PROVISIONING ENDPOINTS ---

@router.post("/telecom/search")
async def search_numbers(
    account_sid: str,
    auth_token: str,
    area_code: str,
    current_user = Depends(get_current_user)
):
    """Search Twilio for available numbers."""
    try:
        numbers = await twilio_service.search_available_numbers(account_sid, auth_token, area_code)
        return {"numbers": numbers}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/telecom/provision")
async def provision_number(
    account_sid: str,
    auth_token: str,
    phone_number: str,
    startup_id: str,
    request: Request,
    language: str = "en-US",
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Buy a Twilio number and save it to the database."""
    try:
        webhook_url = f"https://{request.url.hostname}/api/v1/voice/webhooks/twilio-incoming"
        tw_number = await twilio_service.provision_number(account_sid, auth_token, phone_number, webhook_url)
        
        db_number = ProvisionedNumber(
            startup_id=startup_id,
            provider=TelecomProvider.TWILIO,
            phone_number=tw_number["phone_number"],
            friendly_name=tw_number["friendly_name"],
            sid=tw_number["sid"],
            language=language
        )
        db.add(db_number)
        await db.commit()
        
        return {"status": "success", "number": tw_number}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/telecom/numbers")
async def get_provisioned_numbers(
    startup_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = select(ProvisionedNumber).where(ProvisionedNumber.startup_id == startup_id)
    result = await db.execute(stmt)
    return result.scalars().all()
