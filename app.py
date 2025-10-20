# Fetch and display Google reviews for a Bunnings Warehouse in a specified suburb.
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# --- CONFIGURATION ---
# Load the .env file
load_dotenv()

# Get the API key
API_KEY = os.getenv("API_KEY")

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
    """Fetch and print Google reviews for the given place ID."""
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields=name,rating,user_ratings_total,reviews"
        f"&key={api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if "result" not in data:
        print("❌ No place found or API error:", data.get("status"))
        return

    place = data["result"]
    print(f"\n🏪  {place.get('name')}")
    print(f"⭐  Rating: {place.get('rating')} ({place.get('user_ratings_total')} total)\n")

    reviews = place.get("reviews", [])
    if not reviews:
        print("No reviews available.")
        return

    for i, r in enumerate(reviews, start=1):
        # Convert UNIX timestamp to readable date
        timestamp = r.get("time")
        if timestamp:
            exact_date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        else:
            exact_date = "Unknown"

        print(f"Review {i}:")
        print(f"  Author: {r.get('author_name')}")
        print(f"  Rating: {r.get('rating')}")
        print(f"  Date:   {exact_date}")
        print(f"  Text:   {r.get('text')}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python bunnings_reviews.py <suburb>")
        sys.exit(1)

    suburb = sys.argv[1]
    place_id = get_place_id(suburb, API_KEY)

    if place_id:
        get_bunnings_reviews(place_id, API_KEY)

if __name__ == "__main__":
    main()
