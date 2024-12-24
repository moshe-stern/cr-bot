import re
import time
import traceback
from typing import Union, cast

from playwright.async_api import Page

from src.api import Billing, get_billings, set_billing_payor
from src.classes import BillingUpdateKeys, CRResource
from src.shared import get_cr_session, logger, update_task_progress


async def update_billings(
    parent_task_id: int, child_id: int, resources: list[CRResource], page: Page
):
    cr_session = await get_cr_session()
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }
    for index, resource in enumerate(resources):
        billing_updates = cast(BillingUpdateKeys, resource.updates)
        try:
            billings: list[Billing] = get_billings(
                cr_session,
                resource.id,
                billing_updates.start_date,
                billing_updates.end_date,
            )
            print(len(billings))
            for billing in billings:
                res = set_billing_payor(
                    cr_session, billing["Id"], billing_updates.insurance_id
                )
                if not res["success"]:
                    raise Exception("Failed to set Payor")
                await update_billing(page, billing, billing_updates)
            updated_resources[resource.id] = True
            # update_task_progress(parent_task_id, index + 1, child_id)
        except Exception as e:
            updated_resources[resource.id] = False
            logger.error(f"Failed to update resource {resource.id}: {e}")
            traceback.print_exc()
    return updated_resources


async def update_billing(
    page: Page,
    billing: Billing,
    updates: BillingUpdateKeys,
):
    await page.goto(
        f"https://members.centralreach.com/#billingmanager/timesheeteditor/?&id={billing['Id']}"
    )
    await page.locator("div").filter(
        has_text=re.compile(rf"^ServiceCode{billing['ProcedureCodeString']}$")
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
