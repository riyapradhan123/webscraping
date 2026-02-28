import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path


SOURCES = [
    "https://english.ratopati.com/",
    "https://kathmandupost.com/politics"
]

OUTPUT_FILE = "news.json"


def fetch_headlines(page_url):
    """Download and extract headlines from a webpage."""
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    headlines = []

    try:
        res = requests.get(page_url, headers=headers, timeout=10)
        res.raise_for_status()

        print(f"Connected to {page_url}")

        soup = BeautifulSoup(res.text, "html.parser")

        for tag in soup.select("h2, h3"):
            text = tag.get_text(strip=True)
            if text:
                headlines.append({
                    "headline": text,
                    "scraped_at": datetime.now().isoformat()
                })

        print(f"Extracted {len(headlines)} headlines\n")

    except requests.RequestException as err:
        print(f"Request failed for {page_url}: {err}")

    time.sleep(2)
    return headlines


def load_existing_data():
    """Load JSON data if file exists."""
    
    if not Path(OUTPUT_FILE).exists():
        return {}

    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            content = json.load(file)
            return content if isinstance(content, dict) else {}
    except:
        return {}


def save_data(data):
    """Write updated news data to file."""
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main():
    today_key = datetime.now().strftime("%Y-%m-%d")
    stored_data = load_existing_data()

    if today_key not in stored_data:
        stored_data[today_key] = {}

    for source in SOURCES:
        domain = urlparse(source).netloc
        print(f"Scraping from: {domain}")

        results = fetch_headlines(source)

        stored_data[today_key].setdefault(domain, [])
        stored_data[today_key][domain].extend(results)

    save_data(stored_data)
    print("Scraping complete. Data saved successfully.")


if __name__ == "__main__":
    main()
