import time
from typing import List, Union, cast

from playwright.async_api import Page

from src.api import API
from src.api.auth_settings import load_auth_settings
from src.classes import CRResource, UpdateType, PayorUpdateKeys
from src.services.auth_settings.update_payors import set_global_payer
from src.shared import get_cr_session, handle_dialogs, logger, update_task_progress


async def update_auth_settings(
    parent_task_id: int,
    child_id: int,
    resources_to_update: List[CRResource],
    page: Page,
):
    from src.services import update_payors, update_service_codes

    cr_session = await get_cr_session()
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources_to_update
    }
    for index, resource in enumerate(resources_to_update):
        try:
            await handle_dialogs(page)
            removed_handler = False
            auth_settings = load_auth_settings(cr_session, resource.id)
            updated_settings: bool | None = None
            if len(auth_settings) > 0:
                authorization_page = f"https://members.centralreach.com/#resources/details/?id={resource.id}&tab=authorizations"
                await goto_auth_settings(page, authorization_page)
                for index_2, auth_setting in enumerate(auth_settings):
                    if not removed_handler:
                        time.sleep(2)
                        await handle_dialogs(page, True)
                        removed_handler = True
                    if resource.update_type == UpdateType.PAYORS and index_2 == 0:
                        await set_global_payer(
                            page, cast(PayorUpdateKeys, resource.updates).global_payor
                        )
                    group = page.locator(f"#group-auth-{auth_setting['Id']}")
                    edit = group.locator("a").nth(1)
                    await group.wait_for(state="visible")
                    await group.hover()
                    await edit.click()
                    page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
                    if resource.update_type == UpdateType.PAYORS:
                        updated_settings = await update_payors(resource, page)
                    elif resource.update_type == UpdateType.CODES:
                        updated_settings = await update_service_codes(resource, page)
            updated_resources[resource.id] = updated_settings
        except Exception as e:
            updated_resources[resource.id] = False
            logger.error(f"Failed to update resource {resource.id}: {e}")
        update_task_progress(parent_task_id, index, child_id)
    return updated_resources


async def goto_auth_settings(page: Page, authorization_page):
    await page.goto(authorization_page)
    if (
        page.url != authorization_page
        or await page.locator("text=Resource Not Found").is_visible()
    ):
        raise Exception("Resource does not exist")
