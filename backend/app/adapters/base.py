from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.gateway import IncomingMessage, OutgoingMessage


class ChannelAdapter(ABC):
    """Abstract base class for channel adapters"""
    
    @abstractmethod
    async def parse_incoming(self, raw_message: Dict[str, Any]) -> IncomingMessage:
        """Parse channel-specific message to unified format"""
        pass
    
    @abstractmethod
    async def send_message(self, outgoing: OutgoingMessage) -> bool:
        """Send message through the channel"""
        pass
