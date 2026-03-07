import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.config import settings

logger = logging.getLogger(__name__)


def scrape_all_prices(laptop_name: str) -> dict:
    """
    Runs Flipkart + Croma scrapers in parallel.
    Returns empty results if SCRAPING_ENABLED=false (cloud deployment).
    """
    results = {
        "flipkart": [],
        "croma": [],
        "laptop_name": laptop_name,
        "scraping_enabled": settings.scraping_enabled,
    }

    if not settings.scraping_enabled:
        logger.info("Scraping disabled — skipping price fetch")
        results["note"] = "Live price scraping is disabled in cloud deployment. Run locally to see live prices."
        return results

    # Only import scrapers when scraping is enabled
    # (avoids Selenium import errors on servers without Chrome)
    from app.services.scrapers.flipkart import scrape_flipkart
    from app.services.scrapers.croma import scrape_croma

    scrapers = {
        "flipkart": scrape_flipkart,
        "croma":    scrape_croma,
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
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