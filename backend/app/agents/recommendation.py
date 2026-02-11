from typing import List, Dict, Any
from app.repositories.user_repository import get_user
from app.repositories.product_repository import find_products
import re


async def recommend_products(user_id: str, session_id: str, message: str = "") -> List[Dict[str, Any]]:
    user = await get_user(user_id)
    preferences = user.get("preferences", {}) if user else {}
    
    query_filter = {"stock": {"$gt": 0}}
    
    # Extract query parameters from message
    message_lower = message.lower()
    
    # Check for price constraints
    price_match = re.search(r'under \\$?(\\d+)', message_lower)
    if price_match:
        query_filter["price"] = {"$lte": float(price_match.group(1))}
    elif max_price := preferences.get("max_price"):
        query_filter["price"] = {"$lte": max_price}
    
    # Check for category in message
    categories = ['shoes', 'shirts', 'jeans', 'electronics', 'laptop', 'phone', 'tablet']
    for cat in categories:
        if cat in message_lower:
            query_filter["category"] = {"$regex": cat, "$options": "i"}
            break
    
    # If no category in message, use user preference
    if "category" not in query_filter and (preferred_category := preferences.get("category")):
        query_filter["category"] = preferred_category
    
    # Check for brand in message
    brands = ['nike', 'adidas', 'apple', 'samsung', 'dell', 'hp', 'sony', 'reebok', 'puma', 'lg']
    for brand in brands:
        if brand in message_lower:
            query_filter["name"] = {"$regex": brand, "$options": "i"}
            break
    
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
