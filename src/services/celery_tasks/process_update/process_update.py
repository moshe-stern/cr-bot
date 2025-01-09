import asyncio
import base64
import logging
import os
import tempfile
import traceback

from celery.backends.redis import RedisBackend

from celery_app import celery
from src.classes import UpdateType
from src.services.shared.helpers import (get_data_frame, get_resource_arr,
                                         get_updated_file)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery.task(bind=True, queue="cr-bot-queue")
def process_update(self, file_content: bytes, update_type_str: str, instance: str):
    res = asyncio.run(_process_update(self, file_content, update_type_str, instance))
    if isinstance(res[1], Exception):
        raise Exception(res[1])
    else:
        return res[0]


async def _process_update(self, file_content, update_type_str, instance):
    from src.services.celery_tasks import handle_updates
    from src.services.shared import check_required_cols

    logger.info(f"Starting process_update with type: {update_type_str}")
    try:
        file_data = base64.b64decode(file_content)
        df = get_data_frame(file_data)
        if update_type_str not in UpdateType:
            raise ValueError("Invalid update type specified.")
        update_type = UpdateType(update_type_str)
        check_required_cols(update_type, df)
        resources = get_resource_arr(update_type, df)
        backend: RedisBackend = celery.backend
        task = backend.get_task_meta(self.request.id)
        task_results = task.get("result") or {}
        task_results["total_resources"] = len(resources)
        backend.store_result(self.request.id, task_results, "PENDING")
        results = await handle_updates(
            resources, self.request.id, instance, update_type
        )
        if not results:
            raise Exception("failed to get results")
        is_client_id_col = update_type in [
            UpdateType.SCHEDULE,
            UpdateType.BILLING,
            UpdateType.TIMESHEET,
        ]
        key_column = "client_id" if is_client_id_col else "resource_id"
        updated_file = get_updated_file(df, results, key_column)
        output_folder = "./output"
        os.makedirs(output_folder, exist_ok=True)
        output_file_path = os.path.join(output_folder, os.path.basename("results.xlsx"))
        with open(output_file_path, "wb") as f:
            f.write(updated_file.getvalue())
        logger.info(f"Saved file to {output_file_path}")
        return output_file_path, None
    except Exception as e:
        return "Failed", e
