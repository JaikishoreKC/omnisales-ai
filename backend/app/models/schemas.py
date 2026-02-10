from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class User(BaseModel):
    user_id: str
    name: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    session_id: str
    user_id: str
    last_messages: List[Dict[str, str]] = Field(default_factory=list)
    summary: Optional[str] = None
    cart_items: List[Dict[str, Any]] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Product(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    stock: int


class Order(BaseModel):
    order_id: str
    user_id: str
    items: List[Dict[str, Any]]
    total_price: float
    status: str = "pending"


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    channel: str = "web"


class ChatResponse(BaseModel):
    reply: str
    agent_used: str
    actions: Optional[List[Dict[str, Any]]] = None
