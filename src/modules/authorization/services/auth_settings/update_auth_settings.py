import time
from typing import List, Union
from playwright.sync_api import Page, sync_playwright
from src.actions.auth_settings import load_auth_settings
from src.api import API
from logger_config import logger
from src.modules.shared.log_in import log_in, check_for_multiple_login
from src.modules.shared.start import get_world, start
from src.resources import CRResource


def update_auth_settings(
    celery_task, resources_to_update: List[CRResource], instance: str
):
    with sync_playwright() as p:
        start(p, instance)
        updated_resources: dict[int, Union[bool, None]] = {
            resource.resource_id: None for resource in resources_to_update
        }
        world = get_world()
        page = world.page
        cr_session = world.cr_session
        for index, resource in enumerate(resources_to_update):
            try:
                progress = ((index + 1) / len(resources_to_update)) * 100
                celery_task.update_state(state="PENDING", meta={"progress": progress})
                auth_settings = load_auth_settings(cr_session, resource.resource_id)
                if len(auth_settings) == 0:
                    raise Exception("No authorization settings found")
                authorization_page = f"https://members.centralreach.com/#resources/details/?id={resource.resource_id}&tab=authorizations"
                goto_auth_settings(page, authorization_page)
                for auth_setting in auth_settings:
                    group = page.locator(f"#group-auth-{auth_setting['Id']}")
                    group.wait_for(state="visible")
                    group.hover()
                    edit = group.locator("a").nth(1)
                    edit.wait_for(state="visible")
                    edit.click()
                    page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
                    updated_settings = resource.update(resource)
                    updated_resources[resource.resource_id] = updated_settings
            except Exception as e:
                updated_resources[resource.resource_id] = False
                logger.error(f"Failed to update resource {resource.resource_id}: {e}")
        world.close()
        return updated_resources


def goto_auth_settings(page: Page, authorization_page):
    page.goto(authorization_page)
    if (
        page.url != authorization_page
        or page.locator("text=Resource Not Found").is_visible()
    ):
        raise Exception("Resource does not exist")
    check_for_multiple_login()
