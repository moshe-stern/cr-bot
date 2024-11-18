import time
from asyncio import wait_for
from datetime import datetime
from typing import Union

from playwright.sync_api import sync_playwright

from logger_config import logger
from src.actions.schedule import get_appointments
from src.api import API
from src.modules.shared.log_in import log_in, check_for_multiple_login
from src.modules.shared.start import start, get_world
from src.resources import CRScheduleResource


def update_schedules(celery_task, resources: list[CRScheduleResource], instance: str):
    with sync_playwright() as p:
        updated_resources: dict[int, Union[bool, None]] = {
            resource.client_id: None for resource in resources
        }
        codes_added = 0
        start(p, instance)
        world = get_world()
        page = world.page
        date_today = datetime.now().strftime("%Y-%m-%d")
        for index, resource in enumerate(resources):
            appointments = get_appointments(world.cr_session, resource.client_id)
            progress = ((index + 1) / len(resources)) * 100
            celery_task.update_state(state="PENDING", meta={"progress": progress})
            if len(appointments) == 0:
                raise Exception("No appointments scheduled for this resource")
            try:
                for appointment in appointments:
                    page.goto(
                        f"https://members.centralreach.com/#scheduling/edit/a/{appointment['course']}/dt/{date_today}"
                    )
                    check_for_multiple_login()
                    page.expect_response(API.AUTHORIZATION.LOAD_AUTHS_CODES)
                    deletes_locator = page.get_by_role("button", name="")
                    deletes_locator.first.wait_for(state="visible")
                    deletes = deletes_locator.all()
                    for delete in deletes:
                        delete_locator_2 = page.get_by_role("button", name="")
                        delete_locator_2.first.wait_for(state="visible")
                        delete_locator_2.first.click()
                    page.get_by_role("button", name=" Add").click()
                    items_locator = page.locator(".list-group .list-group-item")
                    items_locator.first.wait_for(state="visible")
                    items_locator.first.wait_for(state="visible")
                    items = items_locator.all()
                    filtered_items = [
                        item
                        for item in items
                        if any(
                            item.get_by_text(code).is_visible()
                            for code in resource.codes
                        )
                    ]
                    for item in filtered_items:
                        item.get_by_role("button", name="Use this").click()
                        codes_added += 1
                    page.get_by_role("button", name="Update Appointment").click()
                    page.get_by_placeholder("Reason for change", exact=True).click()
                    page.get_by_placeholder("Reason for change", exact=True).fill(
                        "Update From Bot"
                    )
                    page.get_by_text("Save", exact=True).click()
                    updated_resources[resource.client_id] = True
            except Exception as e:
                updated_resources[resource.client_id] = False
                logger.error(f"Failed to update resource {resource.client_id}: {e}")
        world.close()
        return updated_resources
