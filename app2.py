import sys
import csv
import requests
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

def get_place_id(suburb: str, api_key: str):
    """Find the Place ID for a Bunnings Warehouse in the given suburb."""
    query = f"Bunnings Warehouse {suburb}"
    url = (
        "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        f"?input={query}&inputtype=textquery&fields=place_id,name,formatted_address"
        f"&key={api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if data.get("status") != "OK" or not data.get("candidates"):
        print(f"❌ Could not find a Bunnings in '{suburb}'. Response: {data.get('status')}")
        return None

    candidate = data["candidates"][0]
    print(f"✅ Found: {candidate.get('name')} ({candidate.get('formatted_address')})")
    return candidate.get("place_id")


def get_bunnings_reviews(place_id: str, api_key: str):
    """Fetch Google reviews and metadata for the given place ID."""
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=name,rating,user_ratings_total,reviews"
        f"&key={api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if "result" not in data:
        print("❌ No place found or API error:", data.get("status"))
        return None, None

    result = data["result"]
    reviews = result.get("reviews", [])
    return result, reviews


def save_reviews_to_csv(suburb: str, store_info: dict, reviews: list):
    """Save reviews and store information to a CSV file."""
    filename = f"bunnings_reviews_{suburb.lower()}_{timestamp}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # --- Store Info ---
        writer.writerow(["Store Name", store_info.get("name", "N/A")])
        writer.writerow(["Store Rating", store_info.get("rating", "N/A")])
        writer.writerow(["Total number of ratings", store_info.get("user_ratings_total", "N/A")])
        writer.writerow([])  # blank line

        # --- Header Row for Reviews ---
        writer.writerow(["Review ID", "Author", "Rating", "Date", "Text"])

        # --- Review Rows ---
        for i, r in enumerate(reviews, start=1):
            writer.writerow([
                i,
                r.get("author_name"),
                r.get("rating"),
                r.get("relative_time_description"),
                r.get("text").replace("\n", " ") if r.get("text") else ""
            ])

    print(f"💾 Saved reviews to: {filename}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python bunnings_reviews.py <suburb>")
        sys.exit(1)

    suburb = sys.argv[1]
    place_id = get_place_id(suburb, API_KEY)

    if not place_id:
        return

    store_info, reviews = get_bunnings_reviews(place_id, API_KEY)

    if store_info and reviews is not None:
        save_reviews_to_csv(suburb, store_info, reviews)
    else:
        print("No data to save.")


if __name__ == "__main__":
    main()
