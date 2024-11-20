from datetime import datetime
from typing import Union

from playwright.async_api import Page

from logger_config import logger
from src.actions.schedule import get_appointments
from src.api import API
from src.modules.shared.helpers.index import NoAppointmentsFound, update_task_progress
from src.modules.shared.log_in import check_for_multiple_login
from src.modules.shared.start import get_cr_session


async def update_schedules(parent_task_id, child_id, resources, page: Page):
    cr_session = get_cr_session()
    updated_resources: dict[int, Union[bool, None]] = {
        resource.client_id: None for resource in resources
    }
    date_today = datetime.now().strftime("%Y-%m-%d")
    for index, resource in enumerate(resources):
        codes_added = 0
        appointments = get_appointments(cr_session, resource.client_id)
        try:
            if len(appointments) == 0:
                raise NoAppointmentsFound("No appointments scheduled for this resource")
            for appointment in appointments:
                await page.goto(
                    f"https://members.centralreach.com/#scheduling/edit/a/{appointment['course']}/dt/{date_today}"
                )
                await check_for_multiple_login(page)
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
                    item
                    for item in items
                    if any(
                        await item.get_by_text(code).is_visible()
                        for code in resource.codes
                    )
                ]
                for item in filtered_items:
                    await item.get_by_role("button", name="Use this").click()
                    codes_added += 1
                await page.get_by_role("button", name="Update Appointment").click()
                await page.get_by_placeholder("Reason for change", exact=True).click()
                await page.get_by_placeholder("Reason for change", exact=True).fill(
                    "Update From Bot"
                )
                await page.get_by_text("Save", exact=True).click()
            updated_resources[resource.client_id] = codes_added == len(resource.codes)
        except NoAppointmentsFound as e:
            logger.error(f"Failed to update resource {resource.client_id}: {e}")
        except Exception as e:
            updated_resources[resource.client_id] = False
            logger.error(f"Failed to update resource {resource.client_id}: {e}")
        update_task_progress(parent_task_id, index + 1, child_id)
    return updated_resources
