from typing import Dict, Any, Optional
from datetime import datetime
from app.repositories.order_repository import get_order
from app.core.database import get_database


async def initiate_return(order_id: str, reason: str, items: list = None) -> Dict[str, Any]:
    """Initiate return request"""
    order = await get_order(order_id)
    
    if not order:
        return {"success": False, "error": "Order not found"}
    
    if order.get("status") == "delivered":
        days_since_delivery = (datetime.utcnow() - order.get("created_at")).days
        if days_since_delivery > 30:
            return {"success": False, "error": "Return window expired (30 days)"}
    
    return_id = f"RET-{order_id[:8]}"
    
    db = get_database()
    return_doc = {
        "return_id": return_id,
        "order_id": order_id,
        "user_id": order.get("user_id"),
        "reason": reason,
        "items": items or order.get("items", []),
        "status": "requested",
        "created_at": datetime.utcnow()
    }
    
    await db.returns.insert_one(return_doc)
    
    return {
        "success": True,
        "return_id": return_id,
        "status": "requested",
        "estimated_refund": order.get("total_price")
    }


async def request_refund(order_id: str) -> Dict[str, Any]:
    """Request refund for order"""
    order = await get_order(order_id)
    
    if not order:
        return {"success": False, "error": "Order not found"}
    
    if order.get("status") not in ["pending", "processing"]:
        return {"success": False, "error": "Order already shipped"}
    
    db = get_database()
    
    # Cancel order and create refund
    await db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"status": "cancelled"}}
    )
    
    refund_id = f"REF-{order_id[:8]}"
    refund_doc = {
        "refund_id": refund_id,
        "order_id": order_id,
        "amount": order.get("total_price"),
        "status": "processing",
        "created_at": datetime.utcnow()
    }
    
    await db.refunds.insert_one(refund_doc)
    
    return {
        "success": True,
        "refund_id": refund_id,
        "amount": order.get("total_price"),
        "estimated_days": "5-7 business days"
    }


async def report_issue(order_id: str, issue_type: str, description: str) -> Dict[str, Any]:
    """Report issue with order"""
    order = await get_order(order_id)
    
    if not order:
        return {"success": False, "error": "Order not found"}
    
    ticket_id = f"TKT-{order_id[:8]}-{datetime.utcnow().strftime('%H%M%S')}"
    
    db = get_database()
    ticket_doc = {
        "ticket_id": ticket_id,
        "order_id": order_id,
        "user_id": order.get("user_id"),
        "issue_type": issue_type,
        "description": description,
        "status": "open",
        "priority": "medium",
        "created_at": datetime.utcnow()
    }
    
    await db.tickets.insert_one(ticket_doc)
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": "open",
        "estimated_response": "24 hours"
    }
