import asyncio
from collections.abc import Callable
from typing import Union, cast

from src.classes import (AIOHTTPClientSession, Billing, BillingUpdateKeys,
                         CRResource)
from src.services.api import get_auth_settings_updates, get_billings_updates


async def get_auth_settings_list(
    client: AIOHTTPClientSession,
    resources: list[CRResource],
    updates: Callable[[CRResource], dict],
):
    return await asyncio.gather(
        *[
            asyncio.create_task(
                get_auth_settings_updates(
                    client,
                    resource.id,
                    updates(resource),
                )
            )
            for resource in resources
        ]
    )
