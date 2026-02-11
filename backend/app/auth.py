"""
Authentication and User Management
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.core.database import get_database

SECRET_KEY = "OPVOdT2UwAKAxH4F7AP0mpyAKCv_5N1a46uorxpbKQw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None


async def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    db = get_database()
    return await db.users.find_one({"email": email})


async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    db = get_database()
    return await db.users.find_one({"user_id": user_id})


async def create_user(email: str, password: str, name: str, role: str = "customer") -> Dict:
    """Create a new user"""
    from uuid import uuid4
    
    db = get_database()
    user = {
        "user_id": str(uuid4()),
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "role": role,  # customer, admin
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    await db.users.create_index("email", unique=True)
    await db.users.insert_one(user)
    
    # Don't return password hash
    user.pop("password_hash")
    return user


async def get_all_users(skip: int = 0, limit: int = 100) -> list:
    """Get all users (admin only)"""
    db = get_database()
    cursor = db.users.find({}, {"password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    return users


async def change_password(user_id: str, old_password: str, new_password: str) -> bool:
    """Change user password (requires old password verification)"""
    db = get_database()
    user = await db.users.find_one({"user_id": user_id})
    
    if not user:
        return False
    
    # Verify old password
    if not verify_password(old_password, user["password_hash"]):
        return False
    
    # Update to new password
    new_hash = hash_password(new_password)
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
    )
    
    return True


async def create_reset_token(email: str) -> Optional[str]:
    """Create a password reset token for a user"""
    user = await get_user_by_email(email)
    if not user:
        return None
    
    # Create token with 1 hour expiration
    token_data = {
        "user_id": user["user_id"],
        "email": email,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


async def reset_password_with_token(token: str, new_password: str) -> bool:
    """Reset password using a valid reset token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return False
        
        user_id = payload.get("user_id")
        if not user_id:
            return False
        
        # Update password
        db = get_database()
        new_hash = hash_password(new_password)
        result = await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
        
    except jwt.InvalidTokenError:
        return False
