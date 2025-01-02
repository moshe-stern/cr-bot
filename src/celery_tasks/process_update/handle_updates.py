import asyncio

from src.classes import CRResource, UpdateType
from src.services.v2 import update_service_codes_v2
from src.shared import divide_list, logger


async def handle_updates(
    resources: list[CRResource], req_id: int, instance: str, update_type: UpdateType
):
    from src.celery_tasks import start_playwright

    chunks = divide_list(resources, 20)
    combined_results: dict = {}
    update_results = []
    logger.info(f"Divided work into {len(chunks)} chunks")
    if update_type == UpdateType.CODES:
        update_results = await asyncio.gather(
            *(update_service_codes_v2(chunk) for chunk in chunks)
        )
        for res in update_results:
            combined_results.update(res)
    else:
        update_results = await start_playwright(chunks, req_id, instance, update_type)
    for result in update_results:
        if isinstance(result, Exception):
            logger.error(f"Error processing chunk: {result}")
        else:
            combined_results.update(result)
    return combined_results
