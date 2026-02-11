from typing import Dict, Any, Optional
from app.repositories.user_repository import get_user
from app.core.database import get_database


async def get_loyalty_points(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user's loyalty points balance"""
    user = await get_user(user_id)
    if not user:
        return None
    
    loyalty = user.get("loyalty", {})
    return {
        "points": loyalty.get("points", 0),
        "tier": loyalty.get("tier", "bronze"),
        "lifetime_value": loyalty.get("lifetime_value", 0)
    }


async def check_offers(user_id: str) -> list:
    """Get available offers for user"""
    db = get_database()
    user = await get_user(user_id)
    
    if not user:
        return []
    
    tier = user.get("loyalty", {}).get("tier", "bronze")
    
    # Fetch offers from database
    offers_collection = db.offers
    cursor = offers_collection.find({
        "active": True,
        "$or": [
            {"tier_required": {"$lte": tier}},
            {"tier_required": None}
        ]
    }).limit(5)
    
    offers = await cursor.to_list(length=5)
    
    return [
        {
            "offer_id": offer.get("offer_id"),
            "title": offer.get("title"),
            "description": offer.get("description"),
            "discount_percent": offer.get("discount_percent"),
            "code": offer.get("code"),
            "expires_at": offer.get("expires_at")
        }
        for offer in offers
    ]


async def redeem_points(user_id: str, points: int) -> Dict[str, Any]:
    """Redeem loyalty points for discount"""
    user = await get_user(user_id)
    
    if not user:
        return {"success": False, "error": "User not found"}
    
    current_points = user.get("loyalty", {}).get("points", 0)
    
    if current_points < points:
        return {"success": False, "error": "Insufficient points"}
    
    # Calculate discount (100 points = $1)
    discount_amount = points / 100
    
    # Update user points
    db = get_database()
    await db.users.update_one(
        {"user_id": user_id},
        {"$inc": {"loyalty.points": -points}}
    )
    
    return {
        "success": True,
        "points_redeemed": points,
        "discount_amount": discount_amount,
        "remaining_points": current_points - points
    }
