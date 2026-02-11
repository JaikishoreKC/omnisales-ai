from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from app.core.database import get_database


async def create_order(user_id: str, items: List[Dict], total_amount: float, shipping_address: Dict) -> Dict:
    """Create a new order"""
    db = get_database()
    
    order = {
        "order_id": str(uuid4()),
        "user_id": user_id,
        "items": items,
        "total_amount": total_amount,
        "shipping_address": shipping_address,
        "status": "pending",
        "payment_status": "paid",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(order)
    return order


async def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.orders.find_one({"order_id": order_id})


async def get_order_by_id(order_id: str) -> Optional[Dict]:
    """Get order by ID"""
    db = get_database()
    return await db.orders.find_one({"order_id": order_id})


async def get_user_orders(user_id: str, limit: int = 50) -> List[Dict]:
    """Get all orders for a user"""
    db = get_database()
    cursor = db.orders.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    orders = await cursor.to_list(length=limit)
    return orders


async def update_order_status(order_id: str, status: str) -> bool:
    db = get_database()
    result = await db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0


async def get_all_orders(skip: int = 0, limit: int = 50) -> List[Dict]:
    """Get all orders (admin)"""
    db = get_database()
    cursor = db.orders.find().sort("created_at", -1).skip(skip).limit(limit)
    orders = await cursor.to_list(length=limit)
    return orders
