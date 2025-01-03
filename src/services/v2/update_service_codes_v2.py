from typing import List, cast, Coroutine
from src.services.api import API
from src.services.api import load_auth_settings, get_service_codes
from src.classes import (
    CRResource,
    ServiceCodeUpdateKeys,
    AuthSetting,
    AIOHTTPClientSession,
)
import asyncio

from src.services.shared import get_cr_session_and_client


async def update_service_codes_v2(resources_to_update: List[CRResource]):
    cr_session, client = await get_cr_session_and_client()

    load_tasks = [
        asyncio.create_task(load_auth_settings(client, resource.id))
        for resource in resources_to_update
    ]
    auth_settings_list: list[list[AuthSetting]] = await asyncio.gather(*load_tasks)
    process_tasks = [
        asyncio.create_task(process_settings(auth_settings, resource, cr_session))
        for auth_settings, resource in zip(auth_settings_list, resources_to_update)
    ]
    updates: list[dict[str, int | bool | None]] = await asyncio.gather(*process_tasks)

    return updates


async def process_settings(
    auth_settings: list[AuthSetting], resource: CRResource, client: AIOHTTPClientSession
):
    service_code_updates = cast(ServiceCodeUpdateKeys, resource.updates)

    async def process_setting(setting: AuthSetting):
        update_tasks = [
            update_codes(code, setting, "SET", client)
            for code in service_code_updates.to_add
        ]
        delete_tasks = [
            update_codes(code, setting, "DELETE", client)
            for code in service_code_updates.to_remove
        ]
        results = await asyncio.gather(*update_tasks, *delete_tasks)
        return {
            "id": resource.id,
            "updated": all(results),
        }

    tasks = [process_setting(setting) for setting in auth_settings]
    resolved = await asyncio.gather(*tasks)
    return resolved


async def update_codes(
    code: str, setting: AuthSetting, update_type: str, client: AIOHTTPClientSession
):
    codes = await get_service_codes(client, code)
    authorization_to_update = [
        auth for auth in setting.Authorizations if auth.ServiceCodeId in codes
    ]
    if not authorization_to_update:
        return None
    api_url = (
        API.AUTHORIZATION.SET if update_type == "SET" else API.AUTHORIZATION.DELETE
    )
    tasks: list[Coroutine] = [
        client.do_cr_post(
            api_url,
            {
                "serviceCodeId": auth.ServiceCodeId,
                "settingsId": auth.authorizationId,
            },
        )
        for auth in authorization_to_update
    ]
    results = await asyncio.gather(*tasks)
    return all(results)
