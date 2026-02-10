from typing import Optional, Dict, Any
from app.core.database import get_database


async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.users.find_one({"user_id": user_id})


async def create_user(user_data: Dict[str, Any]) -> str:
    db = get_database()
    result = await db.users.insert_one(user_data)
    return str(result.inserted_id)


async def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    db = get_database()
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"preferences": preferences}},
        upsert=True
    )
    return result.modified_count > 0
