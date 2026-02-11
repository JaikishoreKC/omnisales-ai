import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect_db(retries: int = 3, delay: float = 0.5):
    global _client, _db
    last_error = None

    for attempt in range(retries):
        try:
            _client = AsyncIOMotorClient(
                settings.mongo_uri,
                serverSelectionTimeoutMS=5000
            )
            _db = _client[settings.db_name]
            await _client.admin.command("ping")
            return
        except Exception as exc:
            last_error = exc
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                continue
            raise RuntimeError("Failed to connect to MongoDB") from last_error


async def close_db():
    global _client
    if _client:
        _client.close()


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() during app startup.")
    return _db
