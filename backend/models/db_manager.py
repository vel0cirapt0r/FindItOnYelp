from peewee import SqliteDatabase
from backend.models.database import database_proxy
from backend.models.models import Business, Location, Category, BusinessCategory, BusinessHours, Attribute
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

            self.db.create_tables([Business, Location, Category, BusinessCategory, BusinessHours, Attribute], safe=True)
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

    def business_exists(self, business_id: str) -> bool:
        """Checks if a business already exists in the database."""
        return Business.select().where(Business.id == business_id).exists()

    def insert_business(self, business_data: dict):
        """Inserts a new business into the database, including location, categories, hours, and attributes."""
        try:
            # Avoid duplicates
            if self.business_exists(business_data["id"]):
                logger.info(f"Business {business_data['name']} already exists, skipping.")
                return

            with self.db.atomic():  # Ensures data consistency
                # Insert business first
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

                # Insert location
                Location.create(
                    business=business,  # 🔹 ForeignKeyField needs the business instance
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

    def get_all_businesses(self):
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
