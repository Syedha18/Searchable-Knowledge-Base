
import asyncio
from src.config.db import get_db
from src.repositories.visual_repository import COLLECTION

async def check():
    db = get_db()
    count = await db[COLLECTION].count_documents({})
    print(f"Total documents in '{COLLECTION}': {count}")

if __name__ == "__main__":
    asyncio.run(check())
