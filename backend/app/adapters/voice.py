import httpx
import logging
from typing import Dict, Any
from app.adapters.base import ChannelAdapter
from app.core.gateway import IncomingMessage, OutgoingMessage, ChannelType
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SUPERU_API_KEY = settings.superu_api_key
SUPERU_API_URL = "https://api.superu.ai/v1/calls"


class VoiceAdapter(ChannelAdapter):
    """SuperU Voice API adapter"""
    
    async def parse_incoming(self, raw_message: Dict[str, Any]) -> IncomingMessage:
        """Parse SuperU webhook payload (transcribed speech)"""
        call_id = raw_message.get("call_id")
        user_phone = raw_message.get("from_number")
        transcript = raw_message.get("transcript", "")
        
        return IncomingMessage(
            channel=ChannelType.VOICE,
            user_id=user_phone,
            session_id=f"voice_{call_id}",
            message=transcript,
            metadata={"call_id": call_id, "raw": raw_message}
        )
    
    async def send_message(self, outgoing: OutgoingMessage) -> bool:
        """Send voice response via SuperU TTS"""
        if not SUPERU_API_KEY:
            return False
        
        headers = {
            "Authorization": f"Bearer {SUPERU_API_KEY}",
            "Content-Type": "application/json"
        }
        
        call_id = outgoing.metadata.get("call_id")
        
        payload = {
            "call_id": call_id,
            "action": "speak",
            "text": outgoing.message,
            "voice": "en-US-Neural2-J"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SUPERU_API_URL}/respond",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"SuperU voice error: {e}", exc_info=True)
            return False
    
    async def initiate_outbound_call(self, to_number: str, message: str) -> Dict[str, Any]:
        """Initiate proactive outbound call via SuperU"""
        if not SUPERU_API_KEY:
            return {"success": False, "error": "No API key"}
        
        headers = {
            "Authorization": f"Bearer {SUPERU_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": to_number,
            "from": settings.superu_from_number,
            "initial_message": message,
            "webhook_url": settings.superu_webhook_url
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SUPERU_API_URL}/initiate",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return {"success": True, "call_id": data.get("call_id")}
        except Exception as e:
            return {"success": False, "error": str(e)}
