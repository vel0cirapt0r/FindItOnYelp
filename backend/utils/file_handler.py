import csv
import os
from datetime import datetime
from backend.utils.logger import logger
from backend.models.models import Business, Location, Category, BusinessCategory, BusinessHours, Attribute


EXPORT_DIR = "exports"


def save_to_csv(filename: str = None):
    """Exports business data from the database to a CSV file."""
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

            # Query all businesses from the database
            for business in Business.select():
                location = business.location  # Get location object
                categories = ", ".join([c.category.category_name for c in business.categories])
                business_hours = "; ".join([f"{h.day}:{h.start_time}-{h.end_time}" for h in business.business_hours])
                attributes = "; ".join([f"{a.key}:{a.value}" for a in business.attributes])

                writer.writerow([
                    business.id, business.name, business.alias, business.rating, business.review_count,
                    business.price, business.phone, business.display_phone, business.is_closed,
                    business.url, business.distance,
                    location.address1 if location else "", location.city if location else "",
                    location.state if location else "", location.zip_code if location else "",
                    location.country if location else "", location.latitude if location else "",
                    location.longitude if location else "",
                    categories, business_hours, attributes
                ])

        logger.info(f"CSV file saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return None
