from datetime import datetime, timedelta
from app.database import get_database

CACHE_EXPIRY_HOURS = 6


async def get_cached_prices(laptop_name: str):
    """Return cached prices if they exist and are not expired."""
    db = get_database()
    cache = db["price_cache"]

    record = await cache.find_one({"laptop_name": laptop_name.lower().strip()})
    if not record:
        return None

    age = datetime.utcnow() - record["cached_at"]
    if age > timedelta(hours=CACHE_EXPIRY_HOURS):
        await cache.delete_one({"laptop_name": laptop_name.lower().strip()})
        return None

    return record["prices"]


async def set_cached_prices(laptop_name: str, prices: dict):
    """Store scraped prices in MongoDB cache."""
    db = get_database()
    cache = db["price_cache"]

    await cache.update_one(
        {"laptop_name": laptop_name.lower().strip()},
        {
            "$set": {
                "laptop_name": laptop_name.lower().strip(),
                "prices": prices,
                "cached_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )