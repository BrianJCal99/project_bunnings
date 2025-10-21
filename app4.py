import sys
import csv
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------

load_dotenv() # Load the .env file

API_KEY = os.getenv("GOOGLE_PLACES_NEW_API_KEY") # Get the API key
SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
DETAILS_URL = "https://places.googleapis.com/v1/places/"

# Create timestamp for file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# -------------------------------
# FUNCTIONS
# -------------------------------
def search_bunnings(suburb):
    """Search for a Bunnings store in a given suburb."""
    query = f"Bunnings {suburb}, Australia"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount"
    }
    data = {"textQuery": query}

    response = requests.post(SEARCH_URL, headers=headers, json=data)
    response.raise_for_status()
    places = response.json().get("places", [])
    
    if not places:
        print(f"No Bunnings found in {suburb}")
        sys.exit(1)

    return places[0]  # Take the first (most relevant) result


def get_reviews(place_id):
    """Fetch reviews for a specific place ID."""
    headers = {
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "displayName,rating,userRatingCount,reviews"
    }

    response = requests.get(f"{DETAILS_URL}{place_id}", headers=headers)
    response.raise_for_status()
    result = response.json()

    reviews = result.get("reviews", [])
    store_name = result.get("displayName", {}).get("text", "Unknown Store")
    store_rating = result.get("rating", "N/A")
    total_ratings = result.get("userRatingCount", 0)

    return store_name, store_rating, total_ratings, reviews


def save_to_csv(suburb, store_name, store_rating, total_ratings, reviews):
    """Save reviews to a CSV file."""
    filename = f"./data/bunnings_reviews_{suburb.lower().replace(' ', '_')}_{timestamp}.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Review ID", "Author", "Rating", "Date", "Text",
            "Store Name", "Store Rating", "Total Ratings"
        ])

        for idx, r in enumerate(reviews, start=1):
            writer.writerow([
                idx,
                r.get("authorAttribution", {}).get("displayName", "Anonymous"),
                r.get("rating", ""),
                r.get("publishTime", ""),
                r.get("text", {}).get("text", ""),
                store_name,
                store_rating,
                total_ratings
            ])

    print(f"✅ Saved {len(reviews)} reviews to {filename}")


# -------------------------------
# MAIN SCRIPT
# -------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bunnings_reviews.py <suburb>")
        sys.exit(1)

    suburb = sys.argv[1]
    print(f"🔍 Searching for Bunnings in {suburb}...")

    place = search_bunnings(suburb)
    place_id = place["id"]

    print(f"🏬 Found: {place['displayName']['text']} ({place['formattedAddress']})")
    print(f"⭐ Rating: {place.get('rating', 'N/A')} ({place.get('userRatingCount', 0)} reviews)")

    store_name, store_rating, total_ratings, reviews = get_reviews(place_id)
    save_to_csv(suburb, store_name, store_rating, total_ratings, reviews)
