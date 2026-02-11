++"""
Seed test data for OmniSales AI
Creates sample orders, users with loyalty points, and offers for testing
"""
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "omnisales")


async def seed_test_data():
    """Seed database with test data"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🌱 Seeding test data...")
    
    # 1. Create test users with loyalty data
    print("\n📦 Creating test users...")
    users = [
        {
            "user_id": "customer_123",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "loyalty": {
                "points": 2500,
                "tier": "gold",
                "lifetime_value": 5420.50
            },
            "preferences": {
                "favorite_category": "shirts",
                "preferred_size": "M"
            },
            "created_at": datetime.utcnow() - timedelta(days=365)
        },
        {
            "user_id": "customer_456",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "phone": "+0987654321",
            "loyalty": {
                "points": 750,
                "tier": "silver",
                "lifetime_value": 1250.00
            },
            "preferences": {
                "favorite_category": "electronics",
                "preferred_size": "L"
            },
            "created_at": datetime.utcnow() - timedelta(days=180)
        },
        {
            "user_id": "customer_789",
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "phone": "+1122334455",
            "loyalty": {
                "points": 150,
                "tier": "bronze",
                "lifetime_value": 320.00
            },
            "preferences": {},
            "created_at": datetime.utcnow() - timedelta(days=30)
        }
    ]
    
    for user in users:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": user},
            upsert=True
        )
    print(f"✅ Created {len(users)} test users with loyalty data")
    
    # 2. Create test orders with various statuses
    print("\n📦 Creating test orders...")
    orders = [
        {
            "order_id": "12345",
            "user_id": "customer_123",
            "items": [
                {"product_id": "PROD001", "name": "Premium Adidas Henley - Beige", "price": 53.84, "quantity": 2},
                {"product_id": "PROD002", "name": "Classic Nike Button-Up - Gray", "price": 68.04, "quantity": 1}
            ],
            "total_price": 175.72,
            "status": "delivered",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "delivered_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "order_id": "12346",
            "user_id": "customer_123",
            "items": [
                {"product_id": "PROD003", "name": "Vintage Nike Power Bank - Navy", "price": 149.38, "quantity": 1}
            ],
            "total_price": 149.38,
            "status": "shipped",
            "created_at": datetime.utcnow() - timedelta(days=3),
            "shipped_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "order_id": "ORD-789",
            "user_id": "customer_456",
            "items": [
                {"product_id": "PROD004", "name": "Vintage Reebok Skinny Jeans - Red", "price": 111.72, "quantity": 1},
                {"product_id": "PROD005", "name": "Vintage Reebok Boots - Red", "price": 77.39, "quantity": 1}
            ],
            "total_price": 189.11,
            "status": "processing",
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "order_id": "67890",
            "user_id": "customer_456",
            "items": [
                {"product_id": "PROD006", "name": "Casual Sony Button-Up - Gray", "price": 38.61, "quantity": 3}
            ],
            "total_price": 115.83,
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "order_id": "ORDER999",
            "user_id": "customer_789",
            "items": [
                {"product_id": "PROD007", "name": "Modern Sony Tank Top - Navy", "price": 61.07, "quantity": 1}
            ],
            "total_price": 61.07,
            "status": "cancelled",
            "created_at": datetime.utcnow() - timedelta(days=5),
            "cancelled_at": datetime.utcnow() - timedelta(days=4)
        }
    ]
    
    for order in orders:
        await db.orders.update_one(
            {"order_id": order["order_id"]},
            {"$set": order},
            upsert=True
        )
    print(f"✅ Created {len(orders)} test orders with various statuses")
    
    # 3. Create loyalty offers
    print("\n🎁 Creating loyalty offers...")
    offers = [
        {
            "offer_id": "OFFER001",
            "title": "20% Off Next Purchase",
            "description": "Get 20% off your next order of $50 or more",
            "discount_percent": 20,
            "code": "WELCOME20",
            "tier_required": "bronze",
            "active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        },
        {
            "offer_id": "OFFER002",
            "title": "Free Shipping",
            "description": "Free shipping on all orders for Silver tier members",
            "discount_percent": 0,
            "code": "FREESHIP",
            "tier_required": "silver",
            "active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        {
            "offer_id": "OFFER003",
            "title": "Gold Member Exclusive: 30% Off",
            "description": "Premium discount for our Gold tier members",
            "discount_percent": 30,
            "code": "GOLD30",
            "tier_required": "gold",
            "active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=90)).isoformat()
        },
        {
            "offer_id": "OFFER004",
            "title": "Buy 2 Get 1 Free",
            "description": "Buy any 2 items, get the lowest priced item free",
            "discount_percent": 0,
            "code": "BOGO",
            "tier_required": None,
            "active": True,
            "expires_at": (datetime.utcnow() + timedelta(days=14)).isoformat()
        }
    ]
    
    for offer in offers:
        await db.offers.update_one(
            {"offer_id": offer["offer_id"]},
            {"$set": offer},
            upsert=True
        )
    print(f"✅ Created {len(offers)} loyalty offers")
    
    # 4. Create sample sessions with cart data
    print("\n🛒 Creating sample shopping sessions...")
    sessions = [
        {
            "session_id": "session_cart_test",
            "user_id": "customer_123",
            "cart": [
                {"product_id": "PROD001", "name": "Premium Adidas Henley - Beige", "price": 53.84, "quantity": 1},
                {"product_id": "PROD002", "name": "Classic Nike Button-Up - Gray", "price": 68.04, "quantity": 2}
            ],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
    ]
    
    for session in sessions:
        await db.sessions.update_one(
            {"session_id": session["session_id"]},
            {"$set": session},
            upsert=True
        )
    print(f"✅ Created {len(sessions)} sample sessions with cart data")
    
    # 5. Summary
    print("\n" + "="*60)
    print("🎉 Test data seeding complete!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • {len(users)} users with loyalty points (bronze/silver/gold)")
    print(f"  • {len(orders)} orders (pending/processing/shipped/delivered/cancelled)")
    print(f"  • {len(offers)} loyalty offers")
    print(f"  • {len(sessions)} shopping sessions with cart data")
    
    print(f"\n✅ Test Queries You Can Try:")
    print(f"  📍 'Track order 12345' - delivered order")
    print(f"  📍 'Where is order 12346' - shipped order")
    print(f"  📍 'Order status for ORD-789' - processing")
    print(f"  🎁 'How many points do I have?' - 2500 points (customer_123)")
    print(f"  🎁 'Show me available offers' - 4 offers")
    print(f"  🎁 'Redeem 500 points' - will work")
    print(f"  🛟 'Return order 12345' - will work (delivered)")
    print(f"  🛟 'Refund order 67890' - will work (pending)")
    print(f"  🛒 'View my cart' - session_cart_test has items")
    
    print(f"\n💡 Remember to use user_id 'customer_123' for best test coverage!")
    print("")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_test_data())
