from typing import Dict, Any
from datetime import datetime, timedelta
from app.adapters.voice import VoiceAdapter
from app.core.database import get_database


async def schedule_follow_up_call(user_id: str, reason: str, scheduled_time: datetime = None) -> Dict[str, Any]:
    """Schedule proactive follow-up call"""
    if not scheduled_time:
        scheduled_time = datetime.utcnow() + timedelta(hours=24)
    
    db = get_database()
    
    # Get user phone number
    user = await db.users.find_one({"user_id": user_id})
    if not user or not user.get("phone"):
        return {"success": False, "error": "No phone number"}
    
    call_schedule = {
        "user_id": user_id,
        "phone": user.get("phone"),
        "reason": reason,
        "scheduled_time": scheduled_time,
        "status": "scheduled",
        "created_at": datetime.utcnow()
    }
    
    result = await db.proactive_calls.insert_one(call_schedule)
    
    return {
        "success": True,
        "schedule_id": str(result.inserted_id),
        "scheduled_time": scheduled_time.isoformat()
    }


async def initiate_abandoned_cart_call(user_id: str, cart_items: list) -> Dict[str, Any]:
    """Call user about abandoned cart"""
    db = get_database()
    user = await db.users.find_one({"user_id": user_id})
    
    if not user or not user.get("phone"):
        return {"success": False, "error": "No phone number"}
    
    # Build message
    item_names = ", ".join([item.get("name", "item") for item in cart_items[:3]])
    message = f"Hi, we noticed you left {len(cart_items)} items in your cart including {item_names}. Would you like to complete your purchase?"
    
    # Initiate call via SuperU
    voice_adapter = VoiceAdapter()
    result = await voice_adapter.initiate_outbound_call(
        to_number=user.get("phone"),
        message=message
    )
    
    if result.get("success"):
        # Log call attempt
        await db.proactive_calls.insert_one({
            "user_id": user_id,
            "type": "abandoned_cart",
            "call_id": result.get("call_id"),
            "status": "initiated",
            "created_at": datetime.utcnow()
        })
    
    return result


async def send_order_confirmation_call(order_id: str) -> Dict[str, Any]:
    """Call to confirm order placement"""
    db = get_database()
    order = await db.orders.find_one({"order_id": order_id})
    
    if not order:
        return {"success": False, "error": "Order not found"}
    
    user = await db.users.find_one({"user_id": order.get("user_id")})
    
    if not user or not user.get("phone"):
        return {"success": False, "error": "No phone number"}
    
    message = f"Your order {order_id} totaling ${order.get('total_price')} has been confirmed and will be delivered in 3-5 business days."
    
    voice_adapter = VoiceAdapter()
    result = await voice_adapter.initiate_outbound_call(
        to_number=user.get("phone"),
        message=message
    )
    
    return result
