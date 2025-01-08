import asyncio
from typing import Union, cast

from src.classes import AIOHTTPClientSession, AuthSetting, CRResource, PayorUpdateKeys
from src.services.shared import get_cr_session

from ...api import set_auth_setting
from .shared import get_auth_settings_list


async def update_payors_v2(resources: list[CRResource]):
    cr_session = await get_cr_session()
    client = AIOHTTPClientSession(cr_session)
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }

    def get_updates(resource: CRResource):
        return {
            "global_payor": cast(PayorUpdateKeys, resource.updates).global_payor,
        }

    async with client.managed_session():
        auth_settings_list = await get_auth_settings_list(
            client, resources, get_updates
        )
        updated_settings: list[dict] = await asyncio.gather(
            *[
                process_settings(auth_setting_dict, client)
                for auth_setting_dict in auth_settings_list
            ]
        )
        for updated in updated_settings:
            resource_id = int(updated.get("id", 0))
            updated_resources[resource_id] = updated.get("updated")
    return updated_resources


async def process_settings(auth_settings_dict: dict, client: AIOHTTPClientSession):
    resource_id = list(auth_settings_dict.keys())[0]
    global_payor = cast(str, auth_settings_dict[resource_id].get("global_payor"))
    settings = cast(list[int], auth_settings_dict[resource_id].get("settings", []))
    return {
        "id": resource_id,
        "updated": all(
            await asyncio.gather(
                *[
                    set_auth_setting(client, setting_id, int(global_payor))
                    for setting_id in settings
                ]
            )
        ),
    }
