import asyncio
from typing import cast

from playwright.async_api import Page, async_playwright, Route
from src.classes import CRResource, UpdateType, CRScheduleResource, CRAuthResource
from src.controllers.services import update_auth_settings, update_schedules
from src.shared import divide_list, logger, start


async def start_playwright(
    req_id: int, instance: str, update_type: UpdateType, resources: list[CRResource]
):
    chunks = divide_list(resources, 5)
    combined_results = {}
    logger.info(f"Divided work into {len(chunks)} chunks")
    async with async_playwright() as p:

        async def handle_route(route: Route):
            await route.abort()

        async def process_chunk_wrapper(chunk: list[CRResource], child_id: int):
            async with await context.new_page() as page:
                return await process_chunk(req_id, child_id, chunk, update_type, page)

        context = await start(p, instance)
        await context.route(
            "https://members.centralreach.com/crxapieks/session-lock/ping",
            handle_route,
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
        await context.close()
        return combined_results


async def process_chunk(
    parent_task_id: int,
    child_id: int,
    chunk: list[CRResource],
    update_type: UpdateType,
    page: Page,
) -> dict[int, bool | None]:
    if update_type == UpdateType.SCHEDULE:
        return await update_schedules(
            parent_task_id, child_id, cast(list[CRScheduleResource], chunk), page
        )
    else:
        return await update_auth_settings(
            parent_task_id, child_id, cast(list[CRAuthResource], chunk), page
        )
