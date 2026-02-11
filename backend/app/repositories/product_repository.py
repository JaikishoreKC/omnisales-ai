from typing import List, Dict, Any, Optional
from app.core.database import get_database


async def find_products(query_filter: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    db = get_database()
    cursor = db.products.find(query_filter).limit(limit)
    return await cursor.to_list(length=limit)


async def find_product_by_name(product_name: str) -> Optional[Dict[str, Any]]:
    """
    Search for a product by name using keyword matching.
    If product_name is "adidas shirt", it will find "Adidas T-Shirt" or "Adidas Dress Shirt".
    """
    db = get_database()
    
    # First try exact substring match
    exact_match = await db.products.find_one({"name": {"$regex": product_name, "$options": "i"}})
    if exact_match:
        return exact_match
    
    # If no exact match, try keyword-based search (all keywords must be present)
    keywords = product_name.split()
    if len(keywords) > 1:
        # Build regex pattern: (?=.*adidas)(?=.*shirt) - positive lookahead for each keyword
        pattern = "".join([f"(?=.*{kw})" for kw in keywords])
        keyword_match = await db.products.find_one({"name": {"$regex": pattern, "$options": "i"}})
        if keyword_match:
            return keyword_match
    
    return None


async def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    db = get_database()
    return await db.products.find_one({"product_id": product_id})
