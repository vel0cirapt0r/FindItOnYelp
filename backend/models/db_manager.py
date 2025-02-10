from peewee import SqliteDatabase, Proxy
from backend.models.models import Business, Location, Category, BusinessCategory, BusinessHours, Attribute
from backend.utils.logger import logger

# Database Proxy for flexibility
database_proxy = Proxy()


def initialize_db(db_path="businesses.db"):
    """Initializes and connects the database."""
    logger.info("Initializing database...")

    db = SqliteDatabase(db_path)
    database_proxy.initialize(db)

    try:
        db.connect()
        logger.info("Database connected successfully.")

        db.create_tables([Business, Location, Category, BusinessCategory, BusinessHours, Attribute], safe=True)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    return db
