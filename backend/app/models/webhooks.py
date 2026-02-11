"""Webhook payload validation models"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional


class WhatsAppWebhookEntry(BaseModel):
    """WhatsApp webhook entry structure"""
    id: str
    changes: List[Dict[str, Any]]


class WhatsAppWebhookPayload(BaseModel):
    """WhatsApp Business API webhook payload"""
    object: str = Field(default="whatsapp_business_account")
    entry: List[WhatsAppWebhookEntry]
    
    @validator('entry')
    def validate_entry(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Entry cannot be empty")
        return v
    
    @validator('object')
    def validate_object_type(cls, v):
        if v != "whatsapp_business_account":
            raise ValueError("Invalid webhook object type")
        return v


class SuperUWebhookPayload(BaseModel):
    """SuperU voice webhook payload"""
    call_id: str = Field(..., description="Unique call identifier")
    from_number: str = Field(..., description="Caller phone number")
    to_number: str = Field(..., description="Recipient phone number")
    status: str = Field(..., description="Call status")
    transcription: Optional[str] = Field(None, description="Voice transcription if available")
    recording_url: Optional[str] = Field(None, description="Recording URL if available")
    duration: Optional[int] = Field(None, description="Call duration in seconds")
    
    @validator('call_id')
    def validate_call_id(cls, v):
        if not v or len(v) < 5:
            raise ValueError("Invalid call ID")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["initiated", "ringing", "answered", "completed", "failed", "busy", "no-answer"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        return v


class ChatRequestValidated(BaseModel):
    """Validated chat request with input sanitization"""
    user_id: str = Field(..., min_length=1, max_length=100)
    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=5000)
    channel: str = Field(default="web")
    
    @validator('message')
    def sanitize_message(cls, v):
        # Remove potentially dangerous characters
        # Allow letters, numbers, spaces, and common punctuation
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()
    
    @validator('user_id', 'session_id')
    def validate_ids(cls, v):
        # Ensure IDs are alphanumeric with hyphens/underscores only
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Invalid ID format")
        return v
    
    @validator('channel')
    def validate_channel(cls, v):
        valid_channels = ["web", "whatsapp", "voice"]
        if v not in valid_channels:
            raise ValueError(f"Invalid channel. Must be one of: {valid_channels}")
        return v
