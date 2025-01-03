from celery_app import celery
from src.services.shared import logger


@celery.task(queue="cleanup_file")
def cleanup_file(file_path):
    import os

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File {file_path} removed successfully.")
    except Exception as e:
        logger.error(f"Failed to remove file {file_path}: {e}")
