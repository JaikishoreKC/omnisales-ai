from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.database import get_database

MAX_MESSAGES = 5


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.sessions.find_one({"session_id": session_id})


async def save_message(session_id: str, role: str, text: str) -> None:
    db = get_database()
    session = await db.sessions.find_one({"session_id": session_id}, {"last_messages": 1})
    if session:
        last_messages = session.get("last_messages", [])
        if last_messages:
            last = last_messages[-1]
            if last.get("role") == role and last.get("text") == text:
                return

    message = {
        "role": role,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "last_messages": {
                    "$each": [message],
                    "$slice": -MAX_MESSAGES
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        },
        upsert=True
    )


async def get_last_messages(session_id: str) -> List[Dict[str, str]]:
    session = await get_session(session_id)
    if not session:
        return []
    return session.get("last_messages", [])


async def update_summary(session_id: str, summary_text: str) -> None:
    db = get_database()
    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"summary": summary_text, "updated_at": datetime.utcnow()}},
        upsert=True
    )


async def get_cart(session_id: str) -> List[Dict[str, Any]]:
    session = await get_session(session_id)
    if not session:
        return []
    return session.get("cart_items", [])


async def update_cart(session_id: str, items: List[Dict[str, Any]]) -> None:
    db = get_database()
    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"cart_items": items, "updated_at": datetime.utcnow()}},
        upsert=True
    )
