import asyncio

from playwright.async_api import BrowserContext, Page, Route, async_playwright

from src.classes import CRResource, UpdateType
from src.services.auth_settings import update_auth_settings
from src.services.billing import update_billings
from src.services.schedule import update_schedules
from src.services.shared import start


async def start_playwright(
    chunks: list[list[CRResource]],
    req_id: int,
    instance: str,
    update_type: UpdateType,
):
    async with async_playwright() as p:
        context = await start(p, instance)
        await context.route(
            "https://members.centralreach.com/crxapieks/session-lock/ping",
            handle_route,
        )
        chunk_results = await asyncio.gather(
            *(
                process_chunk_wrapper(chunk, index + 1, context, req_id, update_type)
                for index, chunk in enumerate(chunks)
            )
        )
        await context.close()
        return chunk_results


async def process_chunk(
    parent_task_id: int,
    child_id: int,
    chunk: list[CRResource],
    update_type: UpdateType,
    page: Page,
) -> dict[int, bool | None]:
    if update_type == UpdateType.SCHEDULE:
        return await update_schedules(parent_task_id, child_id, chunk, page)
    elif update_type == UpdateType.BILLING:
        return await update_billings(parent_task_id, child_id, chunk, page)
    elif update_type == UpdateType.CODES or update_type == UpdateType.PAYORS:
        return await update_auth_settings(parent_task_id, child_id, chunk, page)


async def handle_route(route: Route):
    await route.abort()


async def process_chunk_wrapper(
    chunk: list[CRResource],
    child_id: int,
    context: BrowserContext,
    req_id: int,
    update_type: UpdateType,
):
    async with await context.new_page() as page:
        return await process_chunk(req_id, child_id, chunk, update_type, page)
