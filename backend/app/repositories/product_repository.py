from typing import List, Dict, Any, Optional
from app.core.database import get_database


async def find_products(query_filter: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    db = get_database()
    cursor = db.products.find(query_filter).limit(limit)
    return await cursor.to_list(length=limit)


async def find_product_by_name(product_name: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.products.find_one({"name": {"$regex": product_name, "$options": "i"}})


async def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.products.find_one({"product_id": product_id})
