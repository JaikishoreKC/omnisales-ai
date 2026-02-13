from typing import Dict, Any
import httpx
from app.config import get_settings
settings = get_settings()

POS_API_URL = settings.pos_api_url or "http://localhost:6000"
POS_API_KEY = settings.pos_api_key


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
