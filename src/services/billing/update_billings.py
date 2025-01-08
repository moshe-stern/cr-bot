import asyncio
from typing import Union, cast

from src.classes import AIOHTTPClientSession, Billing, BillingUpdateKeys, CRResource
from src.services.api import set_billing_payors
from src.services.billing.shared import get_billings_list
from src.services.shared import logger
from src.services.shared.start import get_cr_session


async def update_billings(resources: list[CRResource]):
    session = await get_cr_session()
    client = AIOHTTPClientSession(session)
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }

    def get_updates(resource: CRResource):
        return {
            "insurance_company_id": cast(
                BillingUpdateKeys, resource.updates
            ).insurance_id
        }

    async with client.managed_session():
        try:
            billings_list: list[dict[str, Union[list[Billing], int]]] = (
                await get_billings_list(client, resources, get_updates)
            )
            updated_billings: list[dict] = await asyncio.gather(
                *[
                    asyncio.create_task(
                        set_billing_payors(
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
