import asyncio
from collections.abc import Callable
from typing import Union, cast

from src.classes import AIOHTTPClientSession, Billing, BillingUpdateKeys, CRResource
from src.services.api import (
    get_authorizations_in_settings_updates,
    get_settings_updates,
)


async def get_auth_settings_list(
    client: AIOHTTPClientSession,
    resources: list[CRResource],
    updates: Callable[[CRResource], dict],
    get_authorizations: bool = False,
):
    return await asyncio.gather(
        *[
            asyncio.create_task(
                get_authorizations_in_settings_updates(
                    client,
                    resource.id,
                    updates(resource),
                )
                if get_authorizations
                else get_settings_updates(client, resource.id, updates(resource))
            )
            for resource in resources
        ]
    )
