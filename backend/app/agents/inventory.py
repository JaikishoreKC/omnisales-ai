from typing import Optional, Dict, Any
from app.repositories.product_repository import find_product_by_name


async def check_stock(product_name: str) -> Optional[Dict[str, Any]]:
    if not product_name:
        return None
    
    product = await find_product_by_name(product_name)
    
    if not product:
        return None
    
    return {
        "product": {
            "product_id": product.get("product_id"),
            "name": product.get("name"),
            "category": product.get("category"),
            "price": product.get("price")
        },
        "stock": product.get("stock", 0)
    }
