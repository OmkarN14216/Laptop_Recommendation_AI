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


def scrape_flipkart(laptop_name: str) -> list:
    driver = None
    results = []
    try:
        driver = create_driver()
        query = laptop_name.replace(" ", "+")
        url = f"https://www.flipkart.com/search?q={query}&otracker=search&as-show=on&as=off"

        driver.get(url)
        time.sleep(3)

        wait = WebDriverWait(driver, 12)

        # Close login popup if present
        try:
            close_btn = driver.find_element(By.XPATH, "//button[contains(@class,'_2KpZ6l')]")
            close_btn.click()
            time.sleep(0.5)
        except NoSuchElementException:
            pass

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jIjQ8S")))
        cards = driver.find_elements(By.CSS_SELECTOR, "div.jIjQ8S")

        count = 0
        for card in cards:
            if count >= 3:
                break
            try:
                try:
                    name_el = card.find_element(By.CSS_SELECTOR, "div.RG5Slk")
                    name = name_el.text.strip()
                except NoSuchElementException:
                    continue

                if not name:
                    continue

                price = "N/A"
                try:
                    price_el = card.find_element(By.CSS_SELECTOR, "div.hZ3P6w")
                    price = price_el.text.strip()
                except NoSuchElementException:
                    pass

                link = f"https://www.flipkart.com/search?q={query}"
                try:
                    link_el = card.find_element(By.CSS_SELECTOR, "a.k7wcnx")
                    href = link_el.get_attribute("href")
                    if href:
                        link = href if href.startswith("http") else f"https://www.flipkart.com{href}"
                except NoSuchElementException:
                    pass

                results.append({"name": name[:80], "price": price, "link": link})
                count += 1

            except Exception as e:
                logger.debug(f"Flipkart card parse error: {e}")
                continue

    except TimeoutException:
        logger.warning(f"Flipkart timeout for: {laptop_name}")
    except Exception as e:
        logger.error(f"Flipkart scrape error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return results