"""
Create Admin User Script
Run this script to create an initial admin user for the system
"""
import asyncio
from app.core.database import connect_db, close_db
from app.auth import create_user


async def create_admin():
    await connect_db()
    
    try:
        # Create admin user
        admin_user = await create_user(
            email="admin@omnisales.com",
            password="admin123",  # Change this password!
            name="Admin User",
            role="admin"
        )
        
        print("✅ Admin user created successfully!")
        print(f"Email: admin@omnisales.com")
        print(f"Password: admin123")
        print(f"User ID: {admin_user['user_id']}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        print("Admin user may already exist.")
    
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(create_admin())
