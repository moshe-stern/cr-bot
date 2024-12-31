import asyncio

from src.celery_tasks import start_playwright
from src.classes import CRResource, UpdateType
from src.services import update_service_codes_v2
from src.shared import divide_list, logger


async def handle_updates(
    resources: list[CRResource], req_id: int, instance: str, update_type: UpdateType
):
    chunks = divide_list(resources, 5)
    combined_results = {}
    logger.info(f"Divided work into {len(chunks)} chunks")
    if update_type == UpdateType.CODES:
        combined_results = await asyncio.gather(
            *(update_service_codes_v2(chunk) for chunk in chunks)
        )
    else:
        await start_playwright(chunks, req_id, instance, update_type, combined_results)
    return combined_results
