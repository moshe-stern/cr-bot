import time
from asyncio import wait_for
from datetime import datetime

from playwright.sync_api import sync_playwright

from src.actions.schedule import get_appointments
from src.api import API
from src.modules.shared.log_in import log_in
from src.modules.shared.start import start, get_world
from src.modules.shared.world import World
from src.resources import CRScheduleResource


def update_schedule(resources: list[CRScheduleResource]):
    with sync_playwright() as p:
        start(p)
        log_in()
        world = get_world()
        page = world.page
        date_today = datetime.now().strftime("%Y-%m-%d")
        for resource in resources:
            appointments = get_appointments(world.cr_session, resource.client_id)
            for appointment in appointments:
                page.goto(
                    f"https://members.centralreach.com/#scheduling/edit/a/{appointment['course']}/dt/{date_today}"
                )
                deletes_locator = page.get_by_role("button", name="")
                if deletes_locator.first.is_visible():
                    deletes = deletes_locator.all()
                    for delete in deletes:
                        delete.click()
                page.get_by_role("button", name=" Add").click()
                items_locator = page.locator(".list-group .list-group-item")
                if items_locator.first.is_visible():
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
                page.get_by_role("button", name="Update Appointment").click()
                page.get_by_placeholder("Reason for change", exact=True).click()
                page.get_by_placeholder("Reason for change", exact=True).fill(
                    "Update From Bot"
                )
                page.get_by_text("Save", exact=True).click()
                world.close()
