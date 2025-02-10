import requests
import logging
from backend.utils.constants import YELP_API_URL, HEADERS

logger = logging.getLogger(__name__)

def fetch_businesses(term: str, location: str, sort_by: str = "best_match", limit: int = 10, max_results: int = 50):
    """Fetch businesses from Yelp API with pagination to retrieve more than 50 results."""
    all_results = []
    offset = 0

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

        try:
            response = requests.get(YELP_API_URL, headers=HEADERS, params=params)
            response.raise_for_status()  # Raise error for non-200 responses
            data = response.json()

            businesses = [
                {
                    "id": b["id"],
                    "name": b["name"],
                    "rating": b.get("rating", 0),
                    "review_count": b.get("review_count", 0),
                    "address": ", ".join(b["location"]["display_address"]),
                    "url": b["url"]
                }
                for b in data.get("businesses", [])
            ]

            if not businesses:
                break  # No more results to fetch

            all_results.extend(businesses)
            offset += batch_limit

        except requests.RequestException as e:
            logger.error(f"Yelp API request failed: {str(e)}")
            break

    return all_results
