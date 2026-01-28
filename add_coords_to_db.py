import json
import os

from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env so we can reuse MONGO_URI from your Flask app
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/belfast_eats")

client = MongoClient(MONGO_URI)
db = client.get_default_database()
if db.name == "admin":
    # If no default DB in URI, fall back to belfast_eats
    db = client["belfast_eats"]

restaurants = db["restaurants"]

# Path to your JSON file
JSON_PATH = os.path.join(os.path.dirname(__file__), "businesses_with_coords.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    businesses = json.load(f)

# Default Belfast city centre coords for missing ones
DEFAULT_LAT = 54.5973
DEFAULT_LNG = -5.9301

updated = 0
not_found = 0

for biz in businesses:
    biz_id = biz.get("_id")
    if not biz_id:
        continue

    # Use lat/lng from JSON if present, otherwise default to city centre
    lat = biz.get("lat", DEFAULT_LAT)
    lng = biz.get("lng", DEFAULT_LNG)

    result = restaurants.update_one(
        {"_id": biz_id},
        {"$set": {
            "latitude": lat,
            "longitude": lng
        }}
    )

    if result.matched_count == 0:
        not_found += 1
    elif result.modified_count > 0:
        updated += 1

print(f"Updated {updated} restaurants with coordinates.")
print(f"{not_found} JSON entries had no matching restaurant in the DB.")
