from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.database import get_database

MAX_MESSAGES = 5


async def get_session(session_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    db = get_database()
    query = {"session_id": session_id}
    if user_id:
        query["user_id"] = user_id
    return await db.sessions.find_one(query)


async def save_message(
    session_id: str,
    user_id: str,
    role: str,
    text: str,
    agent: Optional[str] = None,
    actions: Optional[List[Dict[str, Any]]] = None
) -> None:
    db = get_database()
    if text is None:
        text = ""
    session = await db.sessions.find_one(
        {"session_id": session_id},
        {"last_messages": 1}
    )
    if session:
        if session.get("user_id") and session.get("user_id") != user_id:
            return
        last_messages = session.get("last_messages", [])
        if last_messages:
            last = last_messages[-1]
            if last.get("role") == role and last.get("text") == text:
                return

    message = {
        "role": role,
        "text": text,
        "content": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    if agent:
        message["agent"] = agent
    if actions:
        safe_actions = [a for a in actions if isinstance(a, dict)]
        if safe_actions:
            message["actions"] = safe_actions
    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$setOnInsert": {
                "session_id": session_id,
                "user_id": user_id
            },
            "$push": {
                "last_messages": {
                    "$each": [message],
                    "$slice": -MAX_MESSAGES
                },
                "all_messages": {
                    "$each": [message],
                    "$slice": -200
                }
            },
            "$set": {"updated_at": datetime.utcnow()}
        },
        upsert=True
    )


async def get_last_messages(session_id: str, user_id: str) -> List[Dict[str, str]]:
    session = await get_session(session_id, user_id)
    if not session:
        return []
    return session.get("last_messages", [])


async def get_chat_history(session_id: str, user_id: str, limit: int = 200) -> List[Dict[str, str]]:
    db = get_database()
    limit = max(1, min(limit, 500))
    session = await db.sessions.find_one(
        {"session_id": session_id, "user_id": user_id},
        {"all_messages": {"$slice": -limit}}
    )
    if not session:
        return []
    return session.get("all_messages", [])


async def update_summary(session_id: str, user_id: str, summary_text: str) -> None:
    db = get_database()
    await db.sessions.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$set": {"summary": summary_text, "updated_at": datetime.utcnow()}},
        upsert=True
    )


