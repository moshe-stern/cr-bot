from src.classes import CRResource, UpdateType
from src.services.billing import update_billings
from src.services.shared import divide_list, logger, start


async def handle_updates(
    resources: list[CRResource], req_id: int, instance: str, update_type: UpdateType
):
    from src.services.celery_tasks import start_playwright

    if update_type == UpdateType.BILLING:
        await start(instance)
        return await update_billings(resources)
    else:
        chunks = divide_list(resources, 5)
        logger.info(f"Divided work into {len(chunks)} chunks")
        return await start_playwright(chunks, req_id, instance, update_type)
