from typing import Dict, Any
import httpx
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

POS_API_URL = settings.pos_api_url or "http://localhost:6000"
POS_API_KEY = settings.pos_api_key


async def sync_inventory_to_pos(product_id: str, quantity: int) -> Dict[str, Any]:
    """Sync inventory update to POS system"""
    if not POS_API_KEY:
        return {"success": False, "error": "POS not configured"}
    
    headers = {
        "Authorization": f"Bearer {POS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "product_id": product_id,
        "quantity": quantity,
        "action": "update_stock"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{POS_API_URL}/inventory/sync",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def create_pos_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create order in POS system"""
    if not POS_API_KEY:
        return {"success": False, "error": "POS not configured"}
    
    headers = {
        "Authorization": f"Bearer {POS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{POS_API_URL}/orders/create",
                headers=headers,
                json=order_data,
                timeout=10.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_pos_inventory(location_id: str = None) -> Dict[str, Any]:
    """Fetch real-time inventory from POS"""
    if not POS_API_KEY:
        return {"success": False, "error": "POS not configured"}
    
    headers = {
        "Authorization": f"Bearer {POS_API_KEY}"
    }
    
    params = {"location_id": location_id} if location_id else {}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{POS_API_URL}/inventory",
                headers=headers,
                params=params,
                timeout=10.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}
