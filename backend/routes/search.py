from fastapi import APIRouter, Query, HTTPException
from backend.utils.logger import logger
from backend.services.yelp_service import fetch_businesses
from backend.utils.file_handler import save_to_csv
from backend.models.db_manager import db_manager

router = APIRouter()

@router.get("/search")
def search_businesses(
        term: str = Query(..., title="Search Term", description="Type of business to search for (e.g., pizza, gym)"),
        location: str = Query(..., title="Location", description="City or region (e.g., New York, San Francisco)"),
        sort_by: str = Query("best_match", title="Sort By", description="Sort by best_match, rating, review_count, or distance"),
        limit: int = Query(10, title="Limit", description="Number of results per request (max 50)"),
        max_results: int = Query(50, title="Max Results", description="Total number of results to retrieve (max 1000)"),
        save: bool = Query(False, title="Save to DB", description="Whether to save results to the database"),
) -> dict:
    """Search businesses on Yelp using the provided term and location, with optional database storage."""
    try:
        max_results = min(max_results, 1000)  # Enforce Yelp's API hard limit
        logger.info(f"Searching Yelp for: term='{term}', location='{location}', sort_by='{sort_by}', limit={limit}, max_results={max_results}")

        results = fetch_businesses(term, location, sort_by, limit, max_results)

        if not results:
            raise HTTPException(status_code=404, detail="No businesses found")

        if save:
            for business in results:
                db_manager.insert_business(business)
            logger.info(f"Saved {len(results)} businesses to the database.")

        return {"businesses": results}
    except Exception as e:
        logger.error(f"Error searching businesses: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/export")
def export_to_csv(
        term: str = Query(None, title="Filter by Term", description="Filter businesses by search term"),
        location: str = Query(None, title="Filter by Location", description="Filter businesses by location")
):
    """Exports businesses to a CSV file, optionally filtering by term or location."""
    try:
        businesses = db_manager.get_all_businesses()

        # Apply filters if provided
        if term:
            businesses = [b for b in businesses if term.lower() in b["name"].lower()]
        if location:
            businesses = [b for b in businesses if location.lower() in b["location"]["city"].lower()]

        if not businesses:
            raise HTTPException(status_code=404, detail="No businesses found to export")

        file_name = f"yelp_export_{term or 'all'}_{location or 'all'}.csv"
        file_path = save_to_csv(filename=file_name, businesses=businesses)
        return {"message": "CSV export successful", "file": file_path}
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
