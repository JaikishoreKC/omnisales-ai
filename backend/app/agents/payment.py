from typing import List, Dict, Any


async def process_payment(user_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not items:
        return {"success": False, "error": "No items provided", "verified": False}

    return {
        "success": False,
        "error": "Payment must be completed via checkout",
        "verified": False
    }
