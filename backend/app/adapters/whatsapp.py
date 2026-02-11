import httpx
import logging
from typing import Dict, Any
from app.adapters.base import ChannelAdapter
from app.core.gateway import IncomingMessage, OutgoingMessage, ChannelType
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

WHATSAPP_API_TOKEN = settings.whatsapp_api_token
WHATSAPP_PHONE_ID = settings.whatsapp_phone_id
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"


class WhatsAppAdapter(ChannelAdapter):
    """WhatsApp Business API adapter"""
    
    async def parse_incoming(self, raw_message: Dict[str, Any]) -> IncomingMessage:
        """Parse WhatsApp webhook payload"""
        entry = raw_message.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])
        
        if not messages:
            raise ValueError("No messages in webhook payload")
        
        msg = messages[0]
        from_number = msg.get("from")
        text = msg.get("text", {}).get("body", "")
        msg_id = msg.get("id")
        
        return IncomingMessage(
            channel=ChannelType.WHATSAPP,
            user_id=from_number,
            session_id=f"wa_{from_number}",
            message=text,
            metadata={"message_id": msg_id, "raw": raw_message}
        )
    
    async def send_message(self, outgoing: OutgoingMessage) -> bool:
        """Send message via WhatsApp Business API"""
        if not WHATSAPP_API_TOKEN:
            return False
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": outgoing.user_id,
            "type": "text",
            "text": {"body": outgoing.message}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    WHATSAPP_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}", exc_info=True)
            return False
