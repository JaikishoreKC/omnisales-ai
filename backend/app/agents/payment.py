from typing import List, Dict, Any
import uuid
from datetime import datetime
from app.repositories.order_repository import create_order


async def process_payment(user_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not items:
        return {"success": False, "error": "No items provided"}
    
    total_price = sum(
        item.get("price", 0.0) * item.get("quantity", 1) 
        for item in items
    )
    
    order_data = {
        "order_id": str(uuid.uuid4()),
        "user_id": user_id,
        "items": items,
        "total_price": round(total_price, 2),
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    await create_order(order_data)
    
    return {
        "success": True,
        "order_id": order_data["order_id"],
        "total_price": order_data["total_price"],
        "status": order_data["status"]
    }
