import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo_admin:password@mongo_db:27017/books?authSource=admin")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
books_collection = db.books
