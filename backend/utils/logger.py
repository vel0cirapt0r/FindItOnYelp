import logging
import sys

def setup_logging():
    """Configures logging settings for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),  # Log to console
            logging.FileHandler("app.log", mode="a", encoding="utf-8")  # Log to a file
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
