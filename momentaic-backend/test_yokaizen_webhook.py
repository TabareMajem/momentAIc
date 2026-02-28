import asyncio
from httpx import AsyncClient
from app.main import app
import structlog

logger = structlog.get_logger()

async def test_inbound_webhook():
    print("test_inbound_yokaizen_webhook")
    
    # Simulate an incoming payload from the ai.yokaizen.com GTM Modal
    payload = {
        "event": "lead.captured",
        "data": {
            "character_id": "ykz_sales_bot_1",
            "lead_email": "prospect@example.com",
            "sentiment": "high_intent",
            "startup_id": "00000000-0000-0000-0000-000000000000" # Dummy string, engine handles failed lookup implicitly
        }
    }
    
    headers = {
        "x-yokaizen-webhook-key": "sk_dev_momentaic_123"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/webhooks/yokaizen", json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
             print("webhook_test_success")
        else:
             print("webhook_test_failed")

if __name__ == "__main__":
    asyncio.run(test_inbound_webhook())
