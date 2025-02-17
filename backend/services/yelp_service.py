import requests
from backend.utils.logger import logger
import time
from backend.utils.constants import YELP_API_URL, HEADERS

def fetch_businesses(
        term: str, location: str, sort_by: str = "best_match",
        limit: int = 10, max_results: int = 50
) -> list[dict]:
    """Fetch businesses from Yelp API with pagination."""
    all_results = []
    offset = 0
    max_results = min(max_results, 1000)  # Yelp API hard limit

    while len(all_results) < max_results:
        remaining = max_results - len(all_results)
        batch_limit = min(remaining, 50)  # Yelp API allows max 50 per request

        params = {
            "term": term,
            "location": location,
            "sort_by": sort_by,
            "limit": batch_limit,
            "offset": offset
        }

        logger.debug(f"Yelp API query parameters: {params}")

        try:
            response = requests.get(YELP_API_URL, headers=HEADERS, params=params)

            if response.status_code == 429:
                logger.warning("Rate limit exceeded. Sleeping for 60 seconds...")
                time.sleep(60)
                continue

            response.raise_for_status()  # Raise error for non-200 responses
            data = response.json()

            businesses = data.get("businesses", [])

            if not businesses:
                break  # No more results to fetch

            for b in businesses:
                business_data = {
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
                }

                all_results.append(business_data)

            offset += batch_limit

        except requests.exceptions.Timeout:
            logger.error("Yelp API request timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
        except requests.RequestException as e:
            logger.error(f"Yelp API request failed: {str(e)}")
            break

    return all_results
