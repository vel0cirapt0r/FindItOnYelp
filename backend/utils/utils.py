from datetime import datetime
import httpx
from backend.utils.logger import logger

def format_datetime(dt):
    """Safely format a datetime object to an ISO 8601 string."""
    if isinstance(dt, datetime):
        return dt.isoformat()  # Standard ISO format
    return str(dt)  # Fallback for unexpected types

def parse_yelp_response(data: dict) -> list[dict]:
    """Extract relevant business data from Yelp API response."""
    businesses = []
    for b in data.get("businesses", []):
        # Extracting location data as a dictionary
        location_data = {
            "address1": b.get("location", {}).get("address1", ""),
            "address2": b.get("location", {}).get("address2", ""),
            "address3": b.get("location", {}).get("address3", ""),
            "city": b.get("location", {}).get("city", ""),
            "state": b.get("location", {}).get("state", ""),
            "zip_code": b.get("location", {}).get("zip_code", ""),
            "country": b.get("location", {}).get("country", ""),
            "latitude": b.get("coordinates", {}).get("latitude", 0.0),
            "longitude": b.get("coordinates", {}).get("longitude", 0.0)
        }

        # Parsing business hours (handling days and time ranges)
        business_hours = []
        for hours in b.get("business_hours", []):
            for open_time in hours.get("open", []):
                business_hours.append({
                    "day": open_time.get("day", ""),
                    "start_time": open_time.get("start", ""),
                    "end_time": open_time.get("end", ""),
                    "is_overnight": open_time.get("is_overnight", False)
                })

        # Parsing attributes (if they exist)
        attributes = b.get("attributes", {})

        # Parsing categories with alias and title
        categories = [{
            "alias": c["alias"],
            "title": c["title"]
        } for c in b.get("categories", [])]

        # Append the business data
        business_dict = {
            "id": b["id"],
            "alias": b.get("alias", ""),
            "name": b["name"],
            "image_url": b.get("image_url", ""),
            "is_closed": b.get("is_closed", False),
            "url": b.get("url", ""),
            "review_count": b.get("review_count", 0),
            "rating": b.get("rating", 0.0),
            "price": b.get("price", ""),
            "phone": b.get("phone", ""),
            "display_phone": b.get("display_phone", ""),
            "distance": b.get("distance", 0.0),
            "location": location_data,
            "categories": categories,
            "business_hours": business_hours,
            "attributes": attributes,
        }

        businesses.append(business_dict)
    return businesses

def handle_rate_limit(response: httpx.Response):
    """Detects if rate limit is exceeded and waits before retrying."""
    if response.status_code == 429:
        logger.warning("Rate limit exceeded. Sleeping for 60 seconds...")
        return True
    return False

def log_request_error(error: Exception):
    """Logs API request errors."""
    if isinstance(error, httpx.TimeoutException):
        logger.error("Yelp API request timed out")
    elif isinstance(error, httpx.HTTPStatusError):
        logger.error(f"HTTP error occurred: {str(error)}")
    elif isinstance(error, httpx.RequestError):
        logger.error(f"Yelp API request failed: {str(error)}")
