import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

YELP_API_KEY = os.getenv("YELP_API_KEY")

if not YELP_API_KEY:
    raise ValueError("Missing YELP_API_KEY in .env file")
