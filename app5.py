import sys
import csv
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_PLACES_NEW_API_KEY")

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
OUTPUT_DIR = "output"
STORES_DIR = "stores"

# Create timestamp for output file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = os.path.join(OUTPUT_DIR, f"bunnings_stores_{timestamp}.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    return places


def process_files():
    """Read suburbs from all state files and write search results to CSV."""
    all_rows = []

    # Go through each file in the stores folder
    for filename in os.listdir(STORES_DIR):
        if not filename.endswith(".txt"):
            continue

        state = os.path.splitext(filename)[0].upper()
        filepath = os.path.join(STORES_DIR, filename)

        print(f"\n📍 Processing file: {filename} ({state})")

        with open(filepath, "r") as f:
            suburbs = [line.strip() for line in f if line.strip()]

        state_count = 0  # counter for this state

        for suburb in suburbs:
            print(f"  🔍 Searching: Bunnings {suburb}")
            try:
                results = search_bunnings(suburb)
                for place in results:
                    all_rows.append({
                        "State": state,
                        "Suburb": suburb,
                        "Store Name": place.get("displayName", {}).get("text", ""),
                        "Address": place.get("formattedAddress", ""),
                        "Store Rating": place.get("rating", ""),
                        "Total Ratings": place.get("userRatingCount", "")
                    })
                    state_count += 1
            except Exception as e:
                print(f"  ⚠️ Error fetching {suburb}: {e}")

        print(f"✅ {state_count} stores data written for {state}")

    # Write all collected data to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["State", "Suburb", "Store Name", "Address", "Store Rating", "Total Ratings"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\n🎉 All data written successfully!")
    print(f"📦 Total stores in CSV: {len(all_rows)}")
    print(f"📁 Output file: {output_file}")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Google API key not found in .env file.")
        sys.exit(1)
    process_files()
