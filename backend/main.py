from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.utils.logger import logger
from backend.routes import search
from backend.models.db_manager import db_manager
from backend.utils.constants import ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown of the database"""
    logger.info("Starting application...")
    db_manager.initialize()  # Initialize database
    yield  # App runs here
    if not db_manager.db.is_closed():
        db_manager.db.close()
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
