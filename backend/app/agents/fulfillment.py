from typing import Optional, Dict, Any
from datetime import timedelta
from app.repositories.order_repository import get_order


async def track_order(order_id: str) -> Optional[Dict[str, Any]]:
    if not order_id:
        return None
    
    order = await get_order(order_id)
    
    if not order:
        return None
    
    status = order.get("status", "unknown")
    created_at = order.get("created_at")
    
    eta = None
    if created_at:
        days_map = {"pending": 1, "processing": 3, "shipped": 5, "delivered": 0}
        eta = created_at + timedelta(days=days_map.get(status, 0))
    
    return {
        "order_id": order.get("order_id"),
        "status": status,
        "eta": eta.isoformat() if eta else None,
        "items": order.get("items", [])
    }
