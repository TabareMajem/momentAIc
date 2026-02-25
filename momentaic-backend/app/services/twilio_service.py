import structlog
from typing import Dict, Any, Optional
from twilio.rest import Client
import os

logger = structlog.get_logger(__name__)

class TwilioService:
    def _get_client(self, account_sid: str, auth_token: str) -> Client:
        return Client(account_sid, auth_token)

    async def search_available_numbers(self, account_sid: str, auth_token: str, area_code: str) -> list:
        """Search Twilio for available phone numbers by area code."""
        try:
            client = self._get_client(account_sid, auth_token)
            numbers = client.available_phone_numbers('US').local.list(
                area_code=area_code,
                limit=5
            )
            return [{"phone_number": n.phone_number, "friendly_name": n.friendly_name} for n in numbers]
        except Exception as e:
            logger.error("Twilio Search Error", error=str(e))
            raise ValueError(f"Failed to search Twilio numbers: {str(e)}")

    async def provision_number(self, account_sid: str, auth_token: str, phone_number: str, webhook_url: str) -> Dict[str, Any]:
        """Buy a phone number and configure its voice webhook."""
        try:
            client = self._get_client(account_sid, auth_token)
            
            # Purchase the number
            incoming_phone_number = client.incoming_phone_numbers.create(
                phone_number=phone_number,
                voice_url=webhook_url,
                voice_method="POST"
            )
            
            return {
                "sid": incoming_phone_number.sid,
                "phone_number": incoming_phone_number.phone_number,
                "friendly_name": incoming_phone_number.friendly_name
            }
        except Exception as e:
            logger.error("Twilio Provisioning Error", error=str(e))
            raise ValueError(f"Failed to provision Twilio number: {str(e)}")

twilio_service = TwilioService()
