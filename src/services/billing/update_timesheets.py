import re
import time
from typing import Union

from playwright.async_api import Page
from typing_extensions import deprecated

from src.classes import (AIOHTTPClientSession, Billing, BillingUpdateKeys,
                         CRResource)
from src.services.shared import get_cr_session


async def update_timesheet(resources: list[CRResource]):
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }
    session = await get_cr_session()
    client = AIOHTTPClientSession(session)

    def get_updates(resource: CRResource):
        return {}

    async with client.managed_session():
        pass
        # billings_list: list[dict[str, Union[list[Billing], int]]] = (
        #     await get_billings_list(client, resources, get_updates)
        # )
        # get_timesheet(client, billings_list[0])
    return updated_resources


@deprecated("This one uses playwright")
async def update_timesheet_old(billing: Billing, updates: Billing, page: Page):
    await page.goto(
        f"https://members.centralreach.com/#billingmanager/timesheeteditor/?&id={billing.id}"
    )
    # await page.locator("div").filter(
    #     has_text=re.compile(rf"^ServiceCode{billing.procedure_code_string}$")
    # ).locator("a").click()
    new_auth = page.locator("a").filter(has_text="kjkkjkj")
    time.sleep(5)
    if await new_auth.is_visible():
        # await page.get_by_test_id("timesheet-placeofservice").select_option(
        #     updates.place_of_service, timeout=1
        # )
        # await page.locator("#selectedServiceAddressId").select_option(
        #     updates.service_address, timeout=1
        # )
        await page.get_by_role("button", name="SUBMIT").click()
