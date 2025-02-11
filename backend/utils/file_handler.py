import csv
import os
from datetime import datetime
from backend.utils.logger import logger

EXPORT_DIR = "exports"

def save_to_csv(filename: str = None, businesses: list = None):
    """Exports given business data (or all businesses if none provided) to a CSV file."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yelp_businesses_{timestamp}.csv"

    filepath = os.path.join(EXPORT_DIR, filename)

    try:
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Define CSV headers
            headers = [
                "id", "name", "alias", "rating", "review_count", "price",
                "phone", "display_phone", "is_closed", "url", "distance",
                "address", "city", "state", "zip_code", "country", "latitude", "longitude",
                "categories", "business_hours", "attributes"
            ]
            writer.writerow(headers)

            # If no businesses provided, fetch all from DB
            if businesses is None:
                from backend.models.db_manager import db_manager
                businesses = db_manager.get_all_businesses()

            for business in businesses:
                location = business["location"] or {}
                categories = ", ".join(business.get("categories", []))
                business_hours = "; ".join([f"{h['day']}:{h['start_time']}-{h['end_time']}" for h in business.get("business_hours", [])])
                attributes = "; ".join([f"{k}:{v}" for k, v in business.get("attributes", {}).items()])

                writer.writerow([
                    business["id"], business["name"], business["alias"], business["rating"], business["review_count"],
                    business.get("price", ""), business["phone"], business["display_phone"], business["is_closed"],
                    business["url"], business["distance"],
                    location.get("address1", ""), location.get("city", ""),
                    location.get("state", ""), location.get("zip_code", ""),
                    location.get("country", ""), location.get("latitude", ""),
                    location.get("longitude", ""),
                    categories, business_hours, attributes
                ])

        logger.info(f"CSV file saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return None
