"""
Review Repository - Database operations for product reviews
"""
from typing import List, Dict, Optional
from datetime import datetime
from uuid import uuid4
from app.database import get_database


async def create_review(product_id: str, user_id: str, user_name: str, rating: int, comment: str) -> Dict:
    """Create a new product review"""
    db = get_database()
    
    review = {
        "review_id": str(uuid4()),
        "product_id": product_id,
        "user_id": user_id,
        "user_name": user_name,
        "rating": rating,  # 1-5
        "comment": comment,
        "created_at": datetime.utcnow(),
        "helpful_count": 0
    }
    
    await db.reviews.insert_one(review)
    return review


async def get_product_reviews(product_id: str, limit: int = 50) -> List[Dict]:
    """Get all reviews for a product"""
    db = get_database()
    cursor = db.reviews.find({"product_id": product_id}).sort("created_at", -1).limit(limit)
    reviews = await cursor.to_list(length=limit)
    return reviews


async def get_review_stats(product_id: str) -> Dict:
    """Get review statistics for a product"""
    db = get_database()
    
    pipeline = [
        {"$match": {"product_id": product_id}},
        {"$group": {
            "_id": None,
            "avg_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1},
            "rating_5": {"$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}},
            "rating_4": {"$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}},
            "rating_3": {"$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}},
            "rating_2": {"$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}},
            "rating_1": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}}
        }}
    ]
    
    result = await db.reviews.aggregate(pipeline).to_list(length=1)
    
    if result:
        stats = result[0]
        stats.pop("_id")
        return stats
    
    return {
        "avg_rating": 0,
        "total_reviews": 0,
        "rating_5": 0,
        "rating_4": 0,
        "rating_3": 0,
        "rating_2": 0,
        "rating_1": 0
    }
