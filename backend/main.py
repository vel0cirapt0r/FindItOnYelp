from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.routes import search

# Initialize FastAPI app
app = FastAPI(title="FindItOnYelp", description="Search businesses on Yelp")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins; restrict if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Include routes
app.include_router(search.router, prefix="/api")

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to FindItOnYelp API"}
