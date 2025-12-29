from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import MONGO_URI, MONGO_DB_NAME

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client[MONGO_DB_NAME]
    return _db
