# Bunnings Google Reviews Scraper

This project collects and analyses Google Reviews for Bunnings Warehouse stores using both the new and old versions of the Google Places API.  
It allows you to search by suburb, fetch store details and reviews, and export them to a CSV file for further analysis.

## Features
- Search for Bunnings stores by suburb
- Retrieve store name, overall rating, and total number of reviews
- Extract individual reviews with author, rating, date, and text
- Export results to a structured CSV file
- Compatible with both legacy and new Google Places APIs

## Requirements
- Python 3.8+
- Google API Key with access to the Places API

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bunnings-reviews-scraper.git
   cd bunnings-reviews-scraper
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the script with a suburb name as a parameter:
```bash
python app.py melbourne
```

This will generate a CSV file containing:
- Review ID  
- Author  
- Rating  
- Date  
- Text  
- Store Name  
- Store Rating  
- Total Number of Ratings  

## Notes
- The Google Places API limits the number of reviews returned per request (usually 5 at a time).
- To collect all reviews, pagination handling may be required.
- Keep your API key secure and avoid sharing it publicly.

## License
This project is open-source and available under the MIT License.
