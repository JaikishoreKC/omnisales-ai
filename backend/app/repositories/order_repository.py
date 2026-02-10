from typing import Optional, Dict, Any
from app.core.database import get_database


async def create_order(order_data: Dict[str, Any]) -> str:
    db = get_database()
    result = await db.orders.insert_one(order_data)
    return str(result.inserted_id)


async def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.orders.find_one({"order_id": order_id})


async def update_order_status(order_id: str, status: str) -> bool:
    db = get_database()
    result = await db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"status": status}}
    )
    return result.modified_count > 0
