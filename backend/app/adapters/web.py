from typing import Dict, Any
from app.adapters.base import ChannelAdapter
from app.core.gateway import IncomingMessage, OutgoingMessage, ChannelType


class WebAdapter(ChannelAdapter):
    """Web chat adapter (existing channel)"""
    
    async def parse_incoming(self, raw_message: Dict[str, Any]) -> IncomingMessage:
        """Parse web chat message"""
        return IncomingMessage(
            channel=ChannelType.WEB,
            user_id=raw_message.get("user_id"),
            session_id=raw_message.get("session_id"),
            message=raw_message.get("message"),
            metadata={}
        )
    
    async def send_message(self, outgoing: OutgoingMessage) -> bool:
        """Web messages returned via HTTP response, not sent separately"""
        return True
