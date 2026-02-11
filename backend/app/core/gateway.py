from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ChannelType(Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    VOICE = "voice"
    MOBILE = "mobile"
    KIOSK = "kiosk"


class IncomingMessage(BaseModel):
    channel: ChannelType
    user_id: str
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OutgoingMessage(BaseModel):
    channel: ChannelType
    user_id: str
    message: str
    actions: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageGateway:
    """Unified gateway to handle messages from all channels"""
    
    def __init__(self):
        self.channel_adapters = {}
    
    def register_adapter(self, channel: ChannelType, adapter):
        """Register a channel-specific adapter"""
        self.channel_adapters[channel] = adapter
    
    async def receive_message(self, channel: ChannelType, raw_message: Dict[str, Any]) -> IncomingMessage:
        """Convert channel-specific message to unified format"""
        adapter = self.channel_adapters.get(channel)
        if not adapter:
            raise ValueError(f"No adapter registered for channel: {channel}")
        
        return await adapter.parse_incoming(raw_message)
    
    async def send_message(self, outgoing: OutgoingMessage) -> bool:
        """Send message through appropriate channel"""
        adapter = self.channel_adapters.get(outgoing.channel)
        if not adapter:
            raise ValueError(f"No adapter registered for channel: {outgoing.channel}")
        
        return await adapter.send_message(outgoing)
