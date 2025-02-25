from peewee import SqliteDatabase, IntegrityError
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
                    rating=business_data.get("rating"),
                    review_count=business_data.get("review_count"),
                    price=business_data.get("price"),
                    phone=business_data.get("phone"),
                    display_phone=business_data.get("display_phone"),
                    is_closed=business_data.get("is_closed"),
                    url=business_data.get("url"),
                    distance=business_data.get("distance")
                )

                # Link Business to SearchTerm
                BusinessSearch.create(search_term=search_term, business=business)

                # Insert location
                location_data = business_data.get("location", {})
                Location.create(
                    business=business,
                    address1=location_data.get("address1"),
                    address2=location_data.get("address2"),
                    address3=location_data.get("address3"),
                    city=location_data.get("city"),
                    state=location_data.get("state"),
                    zip_code=location_data.get("zip_code"),
                    country=location_data.get("country"),
                    latitude=location_data.get("latitude"),
                    longitude=location_data.get("longitude")
                )

                # Insert categories
                for category in business_data.get("categories", []):
                    category_obj, _ = Category.get_or_create(
                        alias=category["alias"],
                        defaults={"title": category["title"]}
                    )
                    BusinessCategory.create(business=business, category=category_obj)

                # Insert business hours
                business_hours_data = business_data.get("business_hours", [])
                for business_hour in business_hours_data:
                    try:
                        BusinessHours.create(
                            business=business,
                            day=business_hour["day"],
                            start_time=business_hour["start_time"],
                            end_time=business_hour["end_time"],
                            is_overnight=business_hour["is_overnight"]
                        )
                    except IntegrityError as e:
                        logger.error(f"BusinessHours insert failed: {e}")

                # Insert attributes
                attributes = business_data.get("attributes", {})
                for key, value in attributes.items():
                    try:
                        if isinstance(value, dict):
                            # Handle nested dictionaries (e.g., 'ambience', 'business_parking')
                            for sub_key, sub_value in value.items():
                                Attribute.create(
                                    business=business,
                                    key=f"{key}_{sub_key}",
                                    value=str(sub_value)
                                )
                        else:
                            Attribute.create(business=business, key=key, value=str(value))
                    except IntegrityError as e:
                        logger.error(f"Attribute insert failed: {e}")

            logger.info(f"Inserted business to database: {business_data['name']}")

        except Exception as e:
            logger.error(f"Error inserting business: {e}")

    @staticmethod
    def insert_search_term(term, location, sort_by, limit, max_results) -> "SearchTerm | None":
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
        if self.is_search_cached(term, location, sort_by):
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
