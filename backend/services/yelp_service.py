import httpx
import asyncio

from backend.models.db_manager import DBManager
from backend.utils.constants import YELP_API_URL, HEADERS
from backend.utils.utils import parse_yelp_response, handle_rate_limit, log_request_error


async def fetch_yelp_data(term: str, location: str, sort_by: str, limit: int, max_results: int) -> list[dict]:
    """Fetch businesses from Yelp API with pagination."""
    all_results = []
    offset = 0
    max_results = min(max_results, 1000)  # Yelp API limit

    async with httpx.AsyncClient() as client:
        while len(all_results) < max_results:
            remaining = max_results - len(all_results)
            batch_limit = min(remaining, limit, 50)

            try:
                response = await client.get(YELP_API_URL, headers=HEADERS, params={
                    "term": term,
                    "location": location,
                    "sort_by": sort_by,
                    "limit": batch_limit,
                    "offset": len(all_results)
                }, timeout=10.0)

                if handle_rate_limit(response):
                    await asyncio.sleep(60)
                    continue

                response.raise_for_status()
                businesses = parse_yelp_response(response.json())

                if not businesses:
                    break

                all_results.extend(businesses)
                offset += batch_limit

            except Exception as e:
                log_request_error(e)
                break

    return all_results

async def get_or_fetch_businesses(term: str, location: str, sort_by: str = "best_match", limit: int = 50, max_results: int = 50):
    """Checks the database cache, otherwise fetches from Yelp API."""
    if DBManager.is_search_cached(term, location, sort_by, limit, max_results):
        return DBManager.get_businesses_for_search(term=term, location=location, sort_by=sort_by)

    businesses = await fetch_yelp_data(term, location, sort_by, limit, max_results)
    if businesses:
        search_term = DBManager.insert_search_term(term, location, sort_by, limit, max_results)
        for business in businesses:
            DBManager.insert_business(business, search_term)
    return businesses
