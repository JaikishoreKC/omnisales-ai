from typing import List, Dict, Any
from app.repositories.user_repository import get_user
from app.repositories.product_repository import find_products


async def recommend_products(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    user = await get_user(user_id)
    preferences = user.get("preferences", {}) if user else {}
    
    query_filter = {"stock": {"$gt": 0}}
    
    if preferred_category := preferences.get("category"):
        query_filter["category"] = preferred_category
    
    if max_price := preferences.get("max_price"):
        query_filter["price"] = {"$lte": max_price}
    
    products = await find_products(query_filter, limit=5)
    
    if len(products) < 5:
        additional = await find_products({"stock": {"$gt": 0}}, limit=5 - len(products))
        products.extend(additional)
    
    return [
        {
            "name": p.get("name"),
            "price": p.get("price"),
            "category": p.get("category")
        }
        for p in products
    ]
