import asyncio
import re
import time
from typing import Any, Union, cast

from playwright.async_api import Page
from typing_extensions import deprecated

from src.classes import AIOHTTPClientSession, Billing, CRResource, TimeSheetUpdateKeys
from src.services.api import is_auth_id_in_billing, set_billing_timesheets
from src.services.billing.shared import get_billings_list
from src.services.shared import get_cr_session


async def update_timesheet(resources: list[CRResource]):
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }
    session = await get_cr_session()
    client = AIOHTTPClientSession(session)

    def get_updates(resource: CRResource):
        return {
            "authorization_id": cast(
                TimeSheetUpdateKeys, resource.updates
            ).authorization_id,
            "provider_id": cast(TimeSheetUpdateKeys, resource.updates).provider_id,
        }

    async with client.managed_session():
        billings_list: list[dict[str, Union[list[Billing], int]]] = (
            await get_billings_list(client, resources, get_updates)
        )
        billings_list = await asyncio.gather(
            *[
                is_auth_id_in_billing(client, billing_dict)
                for billing_dict in billings_list
            ]
        )
        updated_timesheets = await asyncio.gather(
            *[
                asyncio.create_task(set_billing_timesheets(client, billing_dict))
                for billing_dict in billings_list
            ]
        )
        for updated in updated_timesheets:
            for key, value in updated.items():
                updated_resources[key] = value.get("updated")

    return updated_resources


@deprecated("This one uses playwright")
async def update_timesheet_old(billing: Any, updates: Any, page: Page):
    await page.goto(
        f"https://members.centralreach.com/#billingmanager/timesheeteditor/?&id={billing.id}"
    )
    await page.locator("div").filter(
        has_text=re.compile(rf"^ServiceCode{billing.procedure_code_string}$")
    ).locator("a").click()
    new_auth = page.locator("a").filter(has_text="kjkkjkj")
    time.sleep(5)
    if await new_auth.is_visible():
        await page.get_by_test_id("timesheet-placeofservice").select_option(
            updates.place_of_service, timeout=1
        )
        await page.locator("#selectedServiceAddressId").select_option(
            updates.service_address, timeout=1
        )
        await page.get_by_role("button", name="SUBMIT").click()
