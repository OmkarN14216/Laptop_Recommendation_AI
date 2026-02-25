from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from app.services.scraper_service import scrape_all_prices
from app.services.cache_service import get_cached_prices, set_cached_prices

router = APIRouter(tags=["scraper"])


class ScrapeRequest(BaseModel):
    laptop_name: str


@router.post("/prices")
async def get_prices(request: ScrapeRequest):
    laptop_name = request.laptop_name.strip()

    if not laptop_name:
        raise HTTPException(status_code=400, detail="laptop_name is required")

    # Check cache first
    cached = await get_cached_prices(laptop_name)
    if cached:
        return {
            "laptop_name": laptop_name,
            "prices": cached,
            "from_cache": True,
        }

    # Run scraper in thread pool so it doesn't block FastAPI event loop
    loop = asyncio.get_event_loop()
    try:
        prices = await loop.run_in_executor(None, scrape_all_prices, laptop_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    # Cache the results
    await set_cached_prices(laptop_name, prices)

    return {
        "laptop_name": laptop_name,
        "prices": prices,
        "from_cache": False,
    }