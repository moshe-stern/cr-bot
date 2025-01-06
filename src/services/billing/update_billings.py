import asyncio
import re
import time
from typing import Union, cast

from src.classes import AIOHTTPClientSession, Billing, BillingUpdateKeys, CRResource
from src.services.api import get_billings_updates
from src.services.api.billing.billing import set_billing_updates, set_timesheet
from src.services.shared import logger
from src.services.shared.start import get_cr_session


async def update_billings(resources: list[CRResource]):
    session = await get_cr_session()
    client = AIOHTTPClientSession(session)
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }
    async with client.managed_session():
        try:
            billings_list: list[dict[str, Union[list[Billing], int]]] = (
                await asyncio.gather(
                    *[
                        asyncio.create_task(
                            get_billings_updates(
                                client,
                                resource.id,
                                cast(BillingUpdateKeys, resource.updates).start_date,
                                cast(BillingUpdateKeys, resource.updates).end_date,
                                cast(BillingUpdateKeys, resource.updates).insurance_id,
                            )
                        )
                        for resource in resources
                    ]
                )
            )
            updated_billings: list[dict] = await asyncio.gather(
                *[
                    asyncio.create_task(
                        set_billing_updates(
                            client,
                            billing_dict,
                        )
                    )
                    for billing_dict in billings_list
                ]
            )

            for updated in updated_billings:
                for key, value in updated.items():
                    updated_resources[key] = value.get("updated")
            return updated_resources
        except Exception as e:
            logger.error(e)


async def update_timesheet(
    billing: Billing, updates: BillingUpdateKeys, client: AIOHTTPClientSession
):
    pass

    # await page.goto(
    #     f"https://members.centralreach.com/#billingmanager/timesheeteditor/?&id={billing.id}"
    # )
    # await page.locator("div").filter(
    #     has_text=re.compile(rf"^ServiceCode{billing.procedure_code_string}$")
    # ).locator("a").click()
    # new_auth = page.locator("a").filter(has_text="kjkkjkj")
    # time.sleep(5)
    # if await new_auth.is_visible():
    #     await page.get_by_test_id("timesheet-placeofservice").select_option(
    #         updates.place_of_service, timeout=1
    #     )
    #     await page.locator("#selectedServiceAddressId").select_option(
    #         updates.service_address, timeout=1
    #     )
    #     await page.get_by_role("button", name="SUBMIT").click()
