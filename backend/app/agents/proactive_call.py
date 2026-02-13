from typing import Dict, Any
from datetime import datetime, timedelta
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
    if not result.inserted_id:
        return {"success": False, "error": "Failed to schedule call", "verified": False}

    return {
        "success": True,
        "schedule_id": str(result.inserted_id),
        "scheduled_time": scheduled_time.isoformat(),
        "verified": True
    }
