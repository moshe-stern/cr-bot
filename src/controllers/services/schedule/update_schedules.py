from datetime import datetime
from typing import Union, Sequence

from playwright.async_api import Page

from src.actions.schedule import get_appointments
from src.classes import API, CRScheduleResource, CRAuthResource
from src.shared import get_cr_session, handle_dialogs, logger, update_task_progress


async def update_schedules(
    parent_task_id: int,
    child_id: int,
    resources: list[CRScheduleResource],
    page: Page,
):
    cr_session = await get_cr_session()
    updated_resources: dict[int, Union[bool, None]] = {
        resource.client_id: None for resource in resources
    }
    for index, resource in enumerate(resources):
        codes_added = 0
        appointments = get_appointments(cr_session, resource.client_id)
        try:
            if len(appointments) > 0:
                for appointment in appointments:
                    await handle_appointment(appointment, page, codes_added, resource)
                updated_resources[resource.client_id] = (
                    codes_added == len(resource.codes) or None
                )
        except Exception as e:
            updated_resources[resource.client_id] = False
            logger.error(f"Failed to update resource {resource.client_id}: {e}")
        update_task_progress(parent_task_id, index + 1, child_id)
    return updated_resources


async def handle_appointment(
    appointment, page: Page, codes_added: int, resource: CRScheduleResource
):
    date_today = datetime.now().strftime("%Y-%m-%d")
    await handle_dialogs(page)
    removed_handler = False
    await page.goto(
        f"https://members.centralreach.com/#scheduling/edit/a/{appointment['course']}/dt/{date_today}"
    )
    page.expect_response(API.AUTHORIZATION.LOAD_AUTHS_CODES)
    deletes_locator = page.get_by_role("button", name="")
    await deletes_locator.first.wait_for(state="visible")
    deletes = await deletes_locator.all()
    for delete in deletes:
        delete_locator_2 = page.get_by_role("button", name="")
        await delete_locator_2.first.wait_for(state="visible")
        await delete_locator_2.first.click()
    await page.get_by_role("button", name=" Add").click()
    items_locator = page.locator(".list-group .list-group-item")
    await items_locator.first.wait_for(state="visible")
    await items_locator.first.wait_for(state="visible")
    items = await items_locator.all()
    filtered_items = [
        item for item in items if await is_item_visible(item, resource.codes)
    ]
    for item in filtered_items:
        await item.get_by_role("button", name="Use this").click()
        codes_added += 1
    if not removed_handler:
        await handle_dialogs(page, True)
        removed_handler = True
    await page.get_by_role("button", name="Update Appointment").click()
    await page.get_by_placeholder("Reason for change", exact=True).click()
    await page.get_by_placeholder("Reason for change", exact=True).fill(
        "Update From Bot"
    )
    await page.get_by_text("Save", exact=True).click()


async def is_item_visible(item, codes):
    for code in codes:
        if await item.get_by_text(code).is_visible():
            return True
    return False
