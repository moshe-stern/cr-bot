import asyncio
from typing import List, Union, cast

from src.classes import (
    AIOHTTPClientSession,
    AuthSetting,
    CRResource,
    ServiceCodeUpdateKeys,
)
from src.services.api import (
    delete_authorizations_in_setting,
    set_authorization_in_setting,
)
from src.services.shared import get_cr_session

from .shared import get_auth_settings_list


async def update_service_codes_v2(resources: List[CRResource]):
    cr_session = await get_cr_session()
    client = AIOHTTPClientSession(cr_session)
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }

    def get_updates(resource: CRResource):
        return {
            "to_add": cast(ServiceCodeUpdateKeys, resource.updates).to_add,
            "to_remove": cast(ServiceCodeUpdateKeys, resource.updates).to_remove,
        }

    async with client.managed_session():
        auth_settings_list = await get_auth_settings_list(
            client, resources, get_updates, True
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
    to_add = cast(list[str], auth_settings_dict[resource_id].get("to_add"))
    to_remove = cast(list[str], auth_settings_dict[resource_id].get("to_remove"))
    settings = cast(
        list[AuthSetting], auth_settings_dict[resource_id].get("settings", [])
    )

    async def process_setting(setting: AuthSetting):
        return all(
            await asyncio.gather(
                *[
                    delete_authorizations_in_setting(client, setting, int(code))
                    for code in to_remove
                ],
                *[
                    set_authorization_in_setting(client, setting, int(code))
                    for code in to_add
                ]
            )
        )

    return {
        "id": resource_id,
        "updated": all(
            await asyncio.gather(*[process_setting(setting) for setting in settings])
        ),
    }
