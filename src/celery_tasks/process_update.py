import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures.process import ProcessPoolExecutor
from dataclasses import asdict

from celery import Celery, group
import base64
import logging
import tempfile

from playwright.sync_api import sync_playwright

from celery_app import celery
from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.modules.shared.helpers.get_updated_file import get_updated_file
from src.modules.shared.helpers.index import chunk_list
from src.modules.shared.start import start
from src.resources import UpdateType
from src.modules.shared.helpers.get_resource_arr import get_resource_arr
from src.modules.authorization.services.schedule.update_schedules import (
    update_schedules,
)
from src.modules.authorization.services.auth_settings.update_auth_settings import (
    update_auth_settings,
)
from threading import Lock

lock = Lock()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task(bind=True)
def process_update(self, file_content, update_type_str, instance):
    logger.info(f"Starting process_update with type: {update_type_str}")
    try:
        file_data = base64.b64decode(file_content)
        df = get_data_frame(file_data)
        if update_type_str not in UpdateType:
            raise ValueError("Invalid update type specified.")

        update_type = UpdateType(update_type_str)
        resources = get_resource_arr(update_type, df)
        chunks = chunk_list(resources, 3)
        combined_results = {}
        with sync_playwright() as p:
            start(p, instance)
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(process_chunk, self.request.id, chunk, update_type)
                    for chunk in chunks
                ]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        with lock:
                            combined_results.update(result)
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}")
        key_column = (
            "client_id" if update_type == UpdateType.SCHEDULE else "resource_id"
        )
        updated_file = get_updated_file(df, combined_results, key_column)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_file.write(updated_file.getvalue())
            logger.info(f"File saved to {temp_file.name}")
            return temp_file.name
    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={
                "reason": str(e),
                "exc_type": type(e).__name__,
                "exc_message": e.__str__(),
            },
        )
        logger.error(f"Error in process_update: {e}")
        return "Failed"


def process_chunk(parent_task_id, chunk, update_type):
    if update_type == UpdateType.SCHEDULE:
        return update_schedules(parent_task_id, chunk)
    else:
        return update_auth_settings(parent_task_id, chunk)
