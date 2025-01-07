import asyncio
from collections.abc import Callable
from typing import Union, cast

from src.classes import (AIOHTTPClientSession, Billing, BillingUpdateKeys,
                         CRResource)
from src.services.api import get_billings_updates


async def get_billings_list(
    client: AIOHTTPClientSession,
    resources: list[CRResource],
    updates: Callable[[CRResource], dict],
):
    return await asyncio.gather(
        *[
            asyncio.create_task(
                get_billings_updates(
                    client,
                    resource.id,
                    cast(BillingUpdateKeys, resource.updates).start_date,
                    cast(BillingUpdateKeys, resource.updates).end_date,
                    updates(resource),
                )
            )
            for resource in resources
        ]
    )
