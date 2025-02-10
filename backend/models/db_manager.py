from peewee import SqliteDatabase, Proxy
from backend.models.models import Business, Location, Category, BusinessCategory, BusinessHours, Attribute

# Database Proxy for flexibility
database_proxy = Proxy()

def initialize_db(db_path="businesses.db"):
    """Initializes and connects the database."""
    db = SqliteDatabase(db_path)
    database_proxy.initialize(db)
    db.connect()
    db.create_tables([Business, Location, Category, BusinessCategory, BusinessHours, Attribute])
    return db
