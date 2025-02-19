from peewee import SqliteDatabase
from backend.models.database import database_proxy
from backend.models.models import Business, Location, Category, BusinessCategory, BusinessHours, Attribute, SearchTerm, \
    BusinessSearch
from backend.utils.logger import logger


class DBManager:
    """Manages database initialization and operations."""

    def __init__(self, db_path="businesses.db"):
        self.db_path = db_path
        self.db = None

    def initialize(self):
        """Initializes and connects the database."""
        logger.info("Initializing database...")

        self.db = SqliteDatabase(self.db_path)
        database_proxy.initialize(self.db)

        try:
            self.db.connect()
            logger.info("Database connected successfully.")

            self.db.create_tables(
                [
                    SearchTerm,
                    Business,
                    Location,
                    Category,
                    BusinessCategory,
                    BusinessHours,
                    Attribute,
                    BusinessSearch,
                ],
                safe=True
            )
            logger.info("Database tables ensured.")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

        return self.db

    def get_db(self):
        """Returns the database instance."""
        if not self.db:
            self.initialize()
        return self.db

    ### 🔹 Database Operations ###

    @staticmethod
    def is_business_cached(business_id: str) -> bool:
        """Checks if a business already exists in the database."""
        return Business.select().where(Business.id == business_id).exists()

    def insert_business(self, business_data: dict, search_term: SearchTerm):
        """Inserts a new business into the database, linking it to the search term."""
        try:
            # Avoid duplicates
            if self.is_business_cached(business_data["id"]):
                logger.info(f"Business {business_data['name']} already exists, skipping.")
                return

            with self.db.atomic():
                # Insert business
                business = Business.create(
                    id=business_data["id"],
                    name=business_data["name"],
                    alias=business_data["alias"],
                    image_url=business_data.get("image_url"),
                    rating=business_data["rating"],
                    review_count=business_data["review_count"],
                    price=business_data.get("price", None),
                    phone=business_data["phone"],
                    display_phone=business_data["display_phone"],
                    is_closed=business_data["is_closed"],
                    url=business_data["url"],
                    distance=business_data["distance"]
                )

                # Link Business to SearchTerm (New Feature)
                BusinessSearch.create(search_term=search_term, business=business)

                # Insert location
                Location.create(
                    business=business,
                    address1=business_data["address"],
                    city=business_data["city"],
                    state=business_data["state"],
                    zip_code=business_data["zip_code"],
                    country=business_data["country"],
                    latitude=business_data["latitude"],
                    longitude=business_data["longitude"]
                )

                # Insert categories
                for category_name in business_data["categories"]:
                    category, _ = Category.get_or_create(category_name=category_name)
                    BusinessCategory.create(business=business, category=category)

                # Insert business hours
                for hours in business_data.get("hours", []):
                    BusinessHours.create(
                        business=business,
                        day=hours["day"],
                        start_time=hours["start_time"],
                        end_time=hours["end_time"],
                        is_overnight=hours.get("is_overnight", False)
                    )

                # Insert attributes
                for key, value in business_data.get("attributes", {}).items():
                    Attribute.create(business=business, key=key, value=value)

            logger.info(f"Inserted business: {business_data['name']}")
        except Exception as e:
            logger.error(f"Error inserting business: {e}")

    @staticmethod
    def insert_search_term(term, location, sort_by="best_match", limit=10, max_results=50) -> "SearchTerm | None":
        """Stores a search term in the database (if not already present)."""
        try:
            search_term, created = SearchTerm.get_or_create(
                term=term,
                location=location,
                sort_by=sort_by,
                limit=limit,
                max_results=max_results
            )
            return search_term  # Return the object for linking with BusinessSearch
        except Exception as e:
            logger.error(f"Error inserting search term: {e}")
            return None

    @staticmethod
    def is_search_cached(term, location, sort_by="best_match", limit=10, max_results=50) -> bool:
        """Checks if a search term exists in the cache (i.e., has stored businesses)."""
        return SearchTerm.select().where(
            (SearchTerm.term == term) &
            (SearchTerm.location == location) &
            (SearchTerm.sort_by == sort_by)&
            (SearchTerm.limit == limit)&
            (SearchTerm.max_results == max_results)
        ).exists()

    def get_businesses_for_search(self, term, location, sort_by="best_match"):
        """Fetches businesses from cache if the search term exists."""
        if not self.is_search_cached(term, location, sort_by):
            logger.info(f"No cached data for {term} in {location}.")
            return None  # Indicate that fresh data needs to be fetched

        try:
            search_term = SearchTerm.get(
                (SearchTerm.term == term) &
                (SearchTerm.location == location) &
                (SearchTerm.sort_by == sort_by)
            )
            businesses = [bs.business.to_dict() for bs in search_term.businesses]
            return businesses
        except Exception as e:
            logger.error(f"Error fetching businesses for search: {e}")
            return []

    @staticmethod
    def get_all_businesses():
        """Retrieves all businesses with related data."""
        query = Business.select().prefetch(Location, BusinessCategory, Category, BusinessHours, Attribute)
        return [b.to_dict() for b in query]

    def clear_all(self):
        """Deletes all records from all tables."""
        try:
            with self.db.atomic():
                Attribute.delete().execute()
                BusinessHours.delete().execute()
                BusinessCategory.delete().execute()
                Category.delete().execute()
                Location.delete().execute()
                Business.delete().execute()

            logger.info("All database records cleared successfully.")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")


# Singleton instance
db_manager = DBManager()
