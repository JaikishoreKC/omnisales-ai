from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.database import get_database


async def get_cart(owner_type: str, owner_id: str) -> List[Dict[str, Any]]:
    db = get_database()
    cart = await db.carts.find_one({"owner_type": owner_type, "owner_id": owner_id})
    if not cart:
        return []
    return cart.get("items", [])


async def set_cart(owner_type: str, owner_id: str, items: List[Dict[str, Any]]) -> None:
    db = get_database()
    await db.carts.update_one(
        {"owner_type": owner_type, "owner_id": owner_id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}},
        upsert=True,
    )


async def clear_cart(owner_type: str, owner_id: str) -> None:
    await set_cart(owner_type, owner_id, [])


async def add_item(owner_type: str, owner_id: str, item: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = await get_cart(owner_type, owner_id)
    existing = next((i for i in items if i.get("product_id") == item.get("product_id")), None)
    if existing:
        existing["quantity"] = existing.get("quantity", 1) + item.get("quantity", 1)
    else:
        items.append(item)
    await set_cart(owner_type, owner_id, items)
    return items


async def remove_item(owner_type: str, owner_id: str, product_id: str) -> List[Dict[str, Any]]:
    items = await get_cart(owner_type, owner_id)
    items = [i for i in items if i.get("product_id") != product_id]
    await set_cart(owner_type, owner_id, items)
    return items


async def update_quantity(owner_type: str, owner_id: str, product_id: str, quantity: int) -> List[Dict[str, Any]]:
    items = await get_cart(owner_type, owner_id)
    updated = []
    for item in items:
        if item.get("product_id") == product_id:
            if quantity > 0:
                updated.append({**item, "quantity": quantity})
        else:
            updated.append(item)
    await set_cart(owner_type, owner_id, updated)
    return updated
