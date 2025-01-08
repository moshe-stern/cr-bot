from src.classes import CRResource, UpdateType
from src.services.billing import update_billings, update_timesheet
from src.services.shared import divide_list, logger, start
from src.services.v2 import update_payors_v2, update_service_codes_v2
from src.services.v2.schedule.schedule import update_schedules


async def handle_updates(
    resources: list[CRResource], req_id: int, instance: str, update_type: UpdateType
):
    from src.services.celery_tasks import start_playwright

    if update_type == UpdateType.BILLING:
        await start(instance)
        return await update_billings(resources)
    elif update_type == UpdateType.TIMESHEET:
        await start(instance)
        return await update_timesheet(resources)
    elif update_type == UpdateType.CODES:
        await start(instance)
        return await update_service_codes_v2(resources)
    else:
        chunks = divide_list(resources, 5)
        logger.info(f"Divided work into {len(chunks)} chunks")
        return await start_playwright(chunks, req_id, instance, update_type)
