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
            for billing in billings:
                set_billing_payor(cr_session, billing.Id, billing_updates.insurance_id)
                await update_billing(
                    page,
                    billing.Id,
                    billing_updates.authorization_name,
                    billing_updates.place_of_service,
                    billing_updates.service_address,
                )
            updated_resources[resource.id] = True
            update_task_progress(parent_task_id, index + 1, child_id)
        except Exception as e:
            updated_resources[resource.id] = False
            logger.error(f"Failed to update resource {resource.id}: {e}")
    return updated_resources


async def update_billing(
    page: Page,
    billing_id: int,
    authorization: str,
    place_of_service: str,
    service_address: str,
):
    await page.goto(
        f"https://members.centralreach.com/#billingmanager/timesheeteditor/?&id={billing_id}"
    )
    await page.locator(".MuiBox-root > .text-muted").click()
    await page.locator("a").filter(has_text=authorization).click()
    await page.get_by_test_id("timesheet-placeofservice").select_option(
        place_of_service
    )
    await page.locator("#selectedServiceAddressId").select_option(service_address)
    await page.get_by_role("button", name="SUBMIT").click()
