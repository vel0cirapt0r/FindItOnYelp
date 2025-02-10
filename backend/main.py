from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from backend.routes import search
from backend.models.db_manager import initialize_db, database_proxy
from backend.utils.constants import ALLOWED_ORIGINS


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown of the database"""
    logger.info("Starting application...")
    initialize_db()  # Initialize database
    yield  # App runs here
    if not database_proxy.is_closed():
        database_proxy.close()
        logger.info("Database connection closed.")

# Initialize FastAPI app
app = FastAPI(title="FindItOnYelp", description="Search businesses on Yelp", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Allow all origins; restrict if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(search.router, prefix="/api")

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to FindItOnYelp API"}
