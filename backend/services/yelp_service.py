import requests
import logging
import time
from backend.utils.constants import YELP_API_URL, HEADERS

logger = logging.getLogger(__name__)


def fetch_businesses(
        term: str, location: str, sort_by: str = "best_match",
        limit: int = 10, max_results: int = 50
) -> list[dict]:
    """Fetch businesses from Yelp API with pagination to retrieve more than 50 results."""
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

        except requests.exceptions.Timeout:
            logger.error("Yelp API request timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
        except requests.RequestException as e:
            logger.error(f"Yelp API request failed: {str(e)}")
            break

    return all_results
