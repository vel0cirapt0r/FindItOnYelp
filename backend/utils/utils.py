from datetime import datetime
import asyncio
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
        businesses.append({
            "id": b["id"],
            "name": b["name"],
            "alias": b.get("alias", ""),
            "rating": b.get("rating", 0),
            "review_count": b.get("review_count", 0),
            "price": b.get("price", ""),
            "phone": b.get("phone", ""),
            "display_phone": b.get("display_phone", ""),
            "is_closed": b.get("is_closed", False),
            "url": b.get("url", ""),
            "distance": b.get("distance", 0),
            "address": ", ".join(b.get("location", {}).get("display_address", [])),
            "city": b.get("location", {}).get("city", ""),
            "state": b.get("location", {}).get("state", ""),
            "zip_code": b.get("location", {}).get("zip_code", ""),
            "country": b.get("location", {}).get("country", ""),
            "latitude": b.get("coordinates", {}).get("latitude", 0.0),
            "longitude": b.get("coordinates", {}).get("longitude", 0.0),
            "categories": [c["title"] for c in b.get("categories", [])],
        })
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
