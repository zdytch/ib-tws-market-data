from motor import motor_asyncio
from .settings import DB_URL

client = motor_asyncio.AsyncIOMotorClient(DB_URL)
