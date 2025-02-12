import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import database_proxy
from backend.models.models import (
    Business, Location, Category, BusinessCategory, BusinessHours, Attribute
)
from backend.models.db_manager import db_manager
from peewee import SqliteDatabase

# Use an in-memory SQLite database for testing
test_db = SqliteDatabase(":memory:")


@pytest.fixture(scope="module")
def client():
    """Provides a FastAPI test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def setup_test_db():
    """Initializes and clears the test database before each test."""
    # Override the production database with an in-memory test database
    database_proxy.initialize(test_db)
    test_db.connect()
    test_db.create_tables([Business, Location, Category, BusinessCategory, BusinessHours, Attribute])

    yield  # Run the test

    # Cleanup after test
    test_db.drop_tables([Business, Location, Category, BusinessCategory, BusinessHours, Attribute])
    test_db.close()


@pytest.fixture(scope="function")
def clear_database():
    """Clears all database records before and after each test."""
    db_manager.clear_all()  # Clear data before test
    yield
    db_manager.clear_all()  # Clear data after test
