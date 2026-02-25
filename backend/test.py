"""
Test Croma scraper exactly as the real scraper would be called.
Run from backend folder: python test_croma.py
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


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


def test_scrape_croma(laptop_name: str) -> list:
    """Exact same flow as real scraper — takes laptop name, builds URL, scrapes."""
    driver = None
    results = []

    try:
        driver = create_driver()

        # Same URL building as real scraper
        query = laptop_name.replace(" ", "%20")
        url = f"https://www.croma.com/searchB?q={query}%3Arelevance&fromUrl=home"
        print(f"Searching for: '{laptop_name}'")
        print(f"URL: {url}\n")

        driver.get(url)
        time.sleep(3)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, "//li[contains(@class,'product-item')]")))

        cards = driver.find_elements(By.XPATH, "//li[contains(@class,'product-item')]")
        print(f"Found {len(cards)} product cards\n")

        for i, card in enumerate(cards[:3]):
            print(f"{'='*50}")
            print(f"CARD {i+1} — Inspecting structure:")
            print(f"{'='*50}")

            # --- NAME ---
            name = None
            for selector in [
                ".//h3[contains(@class,'product-title')]",
                ".//a[contains(@class,'product-title')]",
                ".//h3",
            ]:
                els = card.find_elements(By.XPATH, selector)
                if els and els[0].text.strip():
                    name = els[0].text.strip()
                    print(f"✅ Name via '{selector}': '{name[:60]}'")
                    break
            if not name:
                print("❌ Name: NOT FOUND")

            # --- PRICE ---
            # value attr has the raw number, text may have ₹ symbol
            price = None
            for selector in [
                ".//span[@id='pdp-product-price']",
                ".//span[@data-testid='new-price']",
                ".//span[contains(@class,'amount')]",
                ".//span[contains(@class,'price')]",
            ]:
                els = card.find_elements(By.XPATH, selector)
                if els:
                    text = els[0].text.strip()
                    value_attr = els[0].get_attribute("value")
                    print(f"✅ Price via '{selector}': text='{text}' | value attr='{value_attr}'")
                    # prefer value attr (raw number), fallback to text
                    if value_attr:
                        price = f"₹{value_attr}"
                    elif text:
                        price = text if text.startswith("₹") else f"₹{text}"
                    break
            if not price:
                print("❌ Price: NOT FOUND")

            # --- LINK --- print ALL anchors so we can see which has /p/ URL
            print("All <a> tags in card:")
            anchors = card.find_elements(By.XPATH, ".//a")
            product_link = None
            for a in anchors:
                href = a.get_attribute("href") or ""
                cls = a.get_attribute("class") or ""
                txt = a.text.strip()[:30]
                print(f"  href='{href[:80]}'")
                print(f"  class='{cls}' | text='{txt}'")
                # Croma product URLs contain /p/ followed by digits
                if "/p/" in href and not product_link:
                    product_link = href
                    print(f"  ⭐ THIS looks like the product link!")
                print()

            if product_link:
                print(f"✅ Link: {product_link}")
            else:
                print("❌ Link: No /p/ URL found in any anchor")

            if name and price:
                results.append({
                    "name": name[:80],
                    "price": price,
                    "link": product_link or f"https://www.croma.com/searchB?q={query}"
                })

            print()

    except TimeoutException:
        print("❌ Timeout — page took too long to load")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    print(f"\n{'='*50}")
    print(f"FINAL RESULTS ({len(results)} items):")
    print(f"{'='*50}")
    for r in results:
        print(f"Name:  {r['name']}")
        print(f"Price: {r['price']}")
        print(f"Link:  {r['link']}")
        print()

    return results


# ---- Run test exactly like real code would ----
if __name__ == "__main__":
    # This is what laptop_service passes after a recommendation
    test_scrape_croma("HP Victus 15")