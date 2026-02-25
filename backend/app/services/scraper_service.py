import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.scrapers.flipkart import scrape_flipkart
from app.services.scrapers.croma import scrape_croma

logger = logging.getLogger(__name__)


def scrape_all_prices(laptop_name: str) -> dict:
    """
    Runs Flipkart, Croma, 
    Returns dict with results from 2 sites.
    """
    results = {
        "flipkart": [],
        "croma": [],
        
        "laptop_name": laptop_name,
    }

    scrapers = {
        "flipkart":        scrape_flipkart,
        "croma":           scrape_croma,
    }

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_site = {
            executor.submit(fn, laptop_name): site
            for site, fn in scrapers.items()
        }
        for future in as_completed(future_to_site):
            site = future_to_site[future]
            try:
                results[site] = future.result()
            except Exception as e:
                logger.error(f"{site} scraper failed: {e}")
                results[site] = []

    return results