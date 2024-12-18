from typing import List, Union

from playwright.async_api import Page

from src.actions.auth_settings import load_auth_settings
from src.classes import API, CRAuthResource
from src.shared import (get_cr_session, handle_dialogs, logger,
                        update_task_progress)


async def update_auth_settings(
    parent_task_id, child_id, resources_to_update: List[CRAuthResource], page: Page
):
    cr_session = await get_cr_session()
    updated_resources: dict[int, Union[bool, None]] = {
        resource.resource_id: None for resource in resources_to_update
    }
    for index, resource in enumerate(resources_to_update):
        try:
            await handle_dialogs(page)
            removed_handler = False
            auth_settings = load_auth_settings(cr_session, resource.resource_id)
            updated_settings: bool | None = None
            if len(auth_settings) > 0:
                authorization_page = f"https://members.centralreach.com/#resources/details/?id={resource.resource_id}&tab=authorizations"
                await goto_auth_settings(page, authorization_page)
                for auth_setting in auth_settings:
                    group = page.locator(f"#group-auth-{auth_setting['Id']}")
                    edit = group.locator("a").nth(1)
                    await group.wait_for(state="visible")
                    if not removed_handler:
                        await handle_dialogs(page, True)
                        removed_handler = True
                    await group.hover()
                    await edit.click()
                    page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
                    updated_settings = await resource.update(resource, page)
            updated_resources[resource.resource_id] = updated_settings
        except Exception as e:
            updated_resources[resource.resource_id] = False
            logger.error(f"Failed to update resource {resource.resource_id}: {e}")
        update_task_progress(parent_task_id, index, child_id)
    return updated_resources


async def goto_auth_settings(page: Page, authorization_page):
    await page.goto(authorization_page)
    if (
        page.url != authorization_page
        or await page.locator("text=Resource Not Found").is_visible()
    ):
        raise Exception("Resource does not exist")
