import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_croma(laptop_name: str) -> list:
    driver = None
    results = []
    try:
        driver = create_driver()
        query = laptop_name.replace(" ", "%20")
        url = f"https://www.croma.com/searchB?q={query}%3Arelevance&fromUrl=home"

        driver.get(url)
        time.sleep(2)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'product-item')]")))

        cards = driver.find_elements(By.XPATH, "//li[contains(@class,'product-item')]")

        count = 0
        for card in cards:
            if count >= 3:
                break
            try:
                try:
                    name_el = card.find_element(By.XPATH, ".//h3[contains(@class,'product-title')]")
                    name = name_el.text.strip()
                    if not name:
                        continue
                except NoSuchElementException:
                    continue

                # FIXED: use data-testid='new-price' (confirmed working in test)
                price = "N/A"
                try:
                    price_el = card.find_element(By.XPATH, ".//span[@data-testid='new-price']")
                    price = price_el.text.strip()
                    if price and not price.startswith("₹"):
                        price = "₹" + price
                except NoSuchElementException:
                    pass

                # FIXED: find first anchor with /p/ in href (confirmed product URL pattern)
                link = f"https://www.croma.com/searchB?q={query}"
                try:
                    anchors = card.find_elements(By.XPATH, ".//a")
                    for a in anchors:
                        href = a.get_attribute("href") or ""
                        if "/p/" in href:
                            link = href
                            break
                except NoSuchElementException:
                    pass

                results.append({"name": name[:80], "price": price, "link": link})
                count += 1

            except Exception as e:
                logger.debug(f"Croma card parse error: {e}")
                continue

    except TimeoutException:
        logger.warning(f"Croma timeout for: {laptop_name}")
    except Exception as e:
        logger.error(f"Croma scrape error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return results