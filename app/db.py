from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://mongo_admin:password@localhost:27017")
db = client.library
books_collection = db.books
