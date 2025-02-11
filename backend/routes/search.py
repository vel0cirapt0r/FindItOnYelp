from fastapi import APIRouter, Query, HTTPException
from backend.utils.logger import logger
from backend.services.yelp_service import fetch_businesses
from backend.utils.file_handler import save_to_csv
from backend.models.db_manager import db_manager
import re


router = APIRouter()

# Store the last search results and search parameters in memory
last_search_results = []
last_search_params = {"term": "", "location": ""}


@router.get("/search")
async def search_businesses(
        term: str = Query(..., title="Search Term", description="Type of business to search for (e.g., pizza, gym)"),
        location: str = Query(..., title="Location", description="City or region (e.g., New York, San Francisco)"),
        sort_by: str = Query("best_match", title="Sort By",
                             description="Sort by best_match, rating, review_count, or distance"),
        limit: int = Query(10, title="Limit", description="Number of results per request (max 50)"),
        max_results: int = Query(50, title="Max Results", description="Total number of results to retrieve (max 1000)"),
        save: bool = Query(False, title="Save to DB", description="Whether to save results to the database"),
) -> dict:
    """Search businesses on Yelp using the provided term and location, with optional database storage."""
    global last_search_results, last_search_params

    try:
        max_results = min(max_results, 1000)  # Enforce Yelp's API hard limit
        logger.info(
            f"Searching Yelp for: term='{term}', location='{location}', sort_by='{sort_by}', limit={limit}, max_results={max_results}")

        results = await fetch_businesses(term, location, sort_by, limit, max_results)

        if not results:
            raise HTTPException(status_code=404, detail="No businesses found")

        # Store the last search results and parameters
        last_search_results = results
        last_search_params = {"term": term, "location": location}

        if save:
            for business in results:
                db_manager.insert_business(business)
            logger.info(f"Saved {len(results)} businesses to the database.")

        return {"businesses": results}

    except Exception as e:
        logger.error(f"Error searching businesses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/export")
def export_to_csv():
    """Exports only the most recent search results to a CSV file with a meaningful name."""
    global last_search_results, last_search_params

    try:
        if not last_search_results and not last_search_params:
            raise HTTPException(status_code=400, detail="No search results to export. Perform a search first.")

        # Generate a clean filename
        term = last_search_params["term"]
        location = last_search_params["location"]

        safe_term = re.sub(r'\W+', '_', term)  # Replace spaces & special chars with '_'
        safe_location = re.sub(r'\W+', '_', location)

        file_name = f"yelp_{safe_term}_{safe_location}.csv"
        file_path = save_to_csv(filename=file_name, businesses=last_search_results)

        return {"message": "CSV export successful", "file": file_path}

    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
