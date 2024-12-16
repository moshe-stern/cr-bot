import asyncio

import base64
import logging
import tempfile

from playwright.async_api import async_playwright, Route

from celery_app import celery
from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.modules.shared.helpers.get_updated_file import get_updated_file
from src.modules.shared.helpers.helpers import divide_list
from src.modules.shared.start import start
from src.classes.resources import UpdateType
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


@celery.task(bind=True, queue="cr-bot-queue")
def process_update(self, file_content, update_type_str, instance):
    res = asyncio.run(_process_update(self, file_content, update_type_str, instance))
    return res


async def _process_update(self, file_content, update_type_str, instance):
    logger.info(f"Starting process_update with type: {update_type_str}")
    try:
        file_data = base64.b64decode(file_content)
        df = get_data_frame(file_data)
        if update_type_str not in UpdateType:
            raise ValueError("Invalid update type specified.")
        update_type = UpdateType(update_type_str)
        resources = get_resource_arr(update_type, df)
        task = celery.backend.get_task_meta(self.request.id)
        task_results = task.get("result") or {}
        task_results["total_resources"] = len(resources)
        celery.backend.store_result(self.request.id, task_results, "PENDING")
        chunks = divide_list(resources, 5)
        logger.info(f"Divided work into {len(chunks)} chunks")
        combined_results = {}
        async with async_playwright() as p:
            context = await start(p, instance)
            async def handle_route(route: Route):
                await route.abort()
            await context.route(
                "https://members.centralreach.com/crxapieks/session-lock/ping",
                handle_route,
            )
            async def process_chunk_wrapper(chunk, child_id):
                """Wrapper to handle chunk processing with its own page."""
                async with await context.new_page() as page:
                    return await process_chunk(
                        self.request.id, child_id, chunk, update_type, page
                    )

            chunk_results = await asyncio.gather(
                *(
                    process_chunk_wrapper(chunk, index + 1)
                    for index, chunk in enumerate(chunks)
                )
            )
            for result in chunk_results:
                if isinstance(result, Exception):
                    logger.error(f"Error processing chunk: {result}")
                else:
                    combined_results.update(result)
            context.close()

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


async def process_chunk(parent_task_id, child_id, chunk, update_type, page):
    if update_type == UpdateType.SCHEDULE:
        return await update_schedules(parent_task_id, child_id, chunk, page)
    else:
        return await update_auth_settings(parent_task_id, child_id, chunk, page)
