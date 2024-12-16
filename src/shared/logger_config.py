import logging

# Set up a basic logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format for log messages
)

# Create a logger instance
logger = logging.getLogger("cr-bot")
