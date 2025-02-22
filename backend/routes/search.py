from fastapi import APIRouter, Query, HTTPException
from backend.utils.logger import logger
from backend.services.yelp_service import get_or_fetch_businesses
from backend.utils.file_handler import save_to_csv
from backend.models.db_manager import DBManager
import re

router = APIRouter()

@router.get("/search")
async def search_businesses(
        term: str = Query(..., title="Search Term", description="Type of business to search for (e.g., pizza, gym)"),
        location: str = Query(..., title="Location", description="City or region (e.g., New York, San Francisco)"),
        sort_by: str = Query("best_match", title="Sort By",
                             description="Sort by best_match, rating, review_count, or distance"),
        limit: int = Query(50, title="Limit", description="Number of results per request (max 50)"),
        max_results: int = Query(50, title="Max Results", description="Total number of results to retrieve (max 1000)"),
) -> dict:
    """Search businesses on Yelp using the provided term and location, with optional database storage."""

    try:
        max_results = min(max_results, 1000)  # Yelp API limit
        logger.info(f"Searching Yelp for: term='{term}', location='{location}', sort_by='{sort_by}', max_results={max_results}")

        results = await get_or_fetch_businesses(term, location, sort_by, limit, max_results)

        if not results:
            raise HTTPException(status_code=404, detail="No businesses found")

        return {"businesses": results}

    except HTTPException as http_exc:
        logger.error(http_exc)
        raise http_exc  # Pass HTTP errors directly
    except Exception as e:
        logger.error(f"Error searching businesses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/export")
def export_to_csv(
    term: str = Query(..., title="Search Term"),
    location: str = Query(..., title="Location"),
    sort_by: str = Query("best_match", title="Sort By"),
    max_results: int = Query(50, title="Max Results")
):
    """Exports the latest search results from the database to a CSV file."""
    try:
        businesses = DBManager.get_businesses_for_search(term, location, sort_by)[:max_results]
        if not businesses:
            raise HTTPException(status_code=400, detail="No search results to export. Perform a search first.")

        # Generate a safe filename
        safe_term = re.sub(r'\W+', '_', term)
        safe_location = re.sub(r'\W+', '_', location)
        safe_sort_by = re.sub(r'\W+', '_', sort_by)
        safe_max_results = re.sub(r'\W+', '_', str(max_results))

        file_name = f"yelp_{safe_term}_{safe_location}_{safe_sort_by}_{safe_max_results}.csv"
        file_path = save_to_csv(filename=file_name, businesses=businesses)

        return {"message": "CSV export successful", "file": file_path}

    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
