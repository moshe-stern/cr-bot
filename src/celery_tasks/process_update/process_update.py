import asyncio
import base64
import logging
import tempfile
import traceback

from celery.backends.redis import RedisBackend

from celery_app import celery
from src.celery_tasks.process_update.start_playwright import start_playwright
from src.classes import UpdateType
from src.shared.helpers import get_data_frame, get_resource_arr, get_updated_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task(bind=True, queue="cr-bot-queue")
def process_update(self, file_content: bytes, update_type_str: str, instance: str):
    return asyncio.run(_process_update(self, file_content, update_type_str, instance))


async def _process_update(self, file_content, update_type_str, instance) -> str:
    logger.info(f"Starting process_update with type: {update_type_str}")
    try:
        file_data = base64.b64decode(file_content)
        df = get_data_frame(file_data)
        if update_type_str not in UpdateType:
            raise ValueError("Invalid update type specified.")
        update_type = UpdateType(update_type_str)
        resources = get_resource_arr(update_type, df)
        backend: RedisBackend = celery.backend
        task = backend.get_task_meta(self.request.id)
        task_results = task.get("result") or {}
        task_results["total_resources"] = len(resources)
        backend.store_result(self.request.id, task_results, "PENDING")
        combined_results = await start_playwright(
            self.request.id, instance, update_type, resources
        )
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
        traceback.print_exc()
        return "Failed"
