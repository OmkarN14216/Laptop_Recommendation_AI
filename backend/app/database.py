from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

# Async client for FastAPI
async_client = None
async_db = None

async def connect_to_mongo():
    global async_client, async_db
    try:
        async_client = AsyncIOMotorClient(settings.mongodb_url)
        async_db = async_client[settings.database_name]
        
        # Test the connection
        await async_client.admin.command('ping')
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    global async_client
    if async_client:
        async_client.close()
        print("❌ Closed MongoDB connection")

def get_database():
    return async_db