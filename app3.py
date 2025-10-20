# Store Bunnings Warehouse ratings from Google Maps into a CSV file.
import requests
import csv
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# --- CONFIGURATION ---
# Load the .env file
load_dotenv()

# Get the API key
API_KEY = os.getenv("API_KEY")

# Create timestamp for file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# --- CONSTANTS ---
SEARCH_QUERY = "Bunnings Warehouse"  # main search term
OUTPUT_FILE = f"bunnings_store_ratings_{timestamp}.csv"

def get_all_bunnings_stores(api_key):
    """
    Fetches all Bunnings stores from Google Places Text Search API,
    following pagination to collect all results.
    """
    stores = []
    next_page_token = None
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    print("🔍 Fetching Bunnings stores from Google Maps...")

    while True:
        params = {
            "query": SEARCH_QUERY,
            "key": api_key,
        }

        if next_page_token:
            params["pagetoken"] = next_page_token
            # Google requires a short delay before using next_page_token
            time.sleep(2)

        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            print(f"⚠️ API Error: {data.get('status')}")
            break

        results = data.get("results", [])
        print(f"✅ Found {len(results)} results in this batch.")

        for place in results:
            stores.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total")
            })

        # Check for more pages
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break

    print(f"\n✅ Total stores collected: {len(stores)}")
    return stores

def save_to_csv(stores, filename):
    """Saves all Bunnings store ratings to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Store Name", "Address", "Rating", "Total Ratings"])

        for s in stores:
            writer.writerow([
                s["name"],
                s["address"],
                s["rating"],
                s["user_ratings_total"]
            ])

    print(f"💾 Data saved to {filename}")

def main():
    stores = get_all_bunnings_stores(API_KEY)
    if stores:
        save_to_csv(stores, OUTPUT_FILE)

if __name__ == "__main__":
    main()
