from fastapi import APIRouter, Query, HTTPException
from backend.utils.logger import logger
from backend.services.yelp_service import fetch_businesses

router = APIRouter()

logger = logger.getLogger(__name__)

@router.get("/search")
def search_businesses(
        term: str = Query(..., title="Search Term", description="Type of business to search for (e.g., pizza, gym)"),
        location: str = Query(..., title="Location", description="City or region (e.g., New York, San Francisco)"),
        sort_by: str = Query("best_match", title="Sort By", description="Sort by best_match, rating, review_count, or distance"),
        limit: int = Query(10, title="Limit", description="Number of results per request (max 50)"),
        max_results: int = Query(50, title="Max Results", description="Total number of results to retrieve (max 1000)"),
) -> dict:
    """Search businesses on Yelp using the provided term and location, with pagination support."""
    try:
        max_results = min(max_results, 1000)  # Enforce Yelp's API hard limit
        logger.info(f"Searching Yelp for: term='{term}', location='{location}', sort_by='{sort_by}', limit={limit}, max_results={max_results}")
        results = fetch_businesses(term, location, sort_by, limit, max_results)

        if not results:
            raise HTTPException(status_code=404, detail="No businesses found")

        return {"businesses": results}
    except Exception as e:
        logger.error(f"Error searching businesses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
