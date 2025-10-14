"""Logger configuration for AI Study Buddy Pro"""
import logging
import os
from ..config import get_config_dict

config = get_config_dict()
LOG_FILE = os.path.join("logs", config["LOG_FILE"])
LOG_LEVEL = config["LOG_LEVEL"]
ENABLE_LOGGING = config["ENABLE_LOGGING"]

def setup_logger():
    """Configure logging for the application"""
    if not ENABLE_LOGGING:
        return

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Create logger
    logger = logging.getLogger('ai_study_buddy')
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Create handlers
    file_handler = logging.FileHandler(LOG_FILE)
    console_handler = logging.StreamHandler()

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logger()