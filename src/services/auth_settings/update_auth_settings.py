import time
from typing import List, Union, cast

from playwright.async_api import Page

from src.classes import (
    API,
    AIOHTTPClientSession,
    AuthSetting,
    CRResource,
    PayorUpdateKeys,
    UpdateType,
)
from src.services.api import load_auth_settings
from src.services.auth_settings.update_payors import set_global_payer
from src.services.shared import handle_dialogs, logger, update_task_progress
from src.services.shared.start import get_cr_session


async def update_auth_settings(
    parent_task_id: int,
    child_id: int,
    resources_to_update: List[CRResource],
    page: Page,
):
    from src.services.auth_settings import update_payors

    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources_to_update
    }
    session = await get_cr_session()
    client = AIOHTTPClientSession(session)
    async with client.managed_session():
        for i, resource in enumerate(resources_to_update):
            try:
                await handle_dialogs(page)
                auth_settings: list[AuthSetting] = await load_auth_settings(
                    client, resource.id
                )
                updated_settings: bool | None = None
                if len(auth_settings) > 0:
                    authorization_page = f"https://members.centralreach.com/#resources/details/?id={resource.id}&tab=authorizations"
                    is_routed = await goto_auth_settings(page, authorization_page)
                    if is_routed:
                        await handle_dialogs(page, True)
                        for j, auth_setting in enumerate(auth_settings):
                            if j == 0:
                                res = await set_global_payer(
                                    page,
                                    cast(
                                        PayorUpdateKeys, resource.updates
                                    ).global_payor,
                                )
                                if not res:
                                    raise Exception("Failed to Set global payor")
                            group = page.locator(f"#group-auth-{auth_setting.id}")
                            edit = group.locator("a").nth(1)
                            await group.wait_for(state="visible")
                            await group.hover()
                            await edit.click()
                            page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
                            updated_settings = await update_payors(resource, page)
                updated_resources[resource.id] = updated_settings
            except Exception as e:
                updated_resources[resource.id] = False
                logger.error(f"Failed to update resource {resource.id}: {e}")
            update_task_progress(parent_task_id, i, child_id)
    return updated_resources


async def goto_auth_settings(page: Page, authorization_page):
    await page.goto(authorization_page)
    if (
        page.url != authorization_page
        or await page.locator("text=Resource Not Found").is_visible()
    ):
        return False
    return True
