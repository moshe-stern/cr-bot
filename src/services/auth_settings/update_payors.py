import json
import time
from typing import cast

from playwright.async_api import Page, Request, Response, Route

from src.classes import API, CRResource, PayorUpdateKeys
from src.services.shared import logger


async def update_payors(payor_resource: CRResource, page: Page):
    resource_global_payer = cast(PayorUpdateKeys, payor_resource.updates).global_payor

    async def add_payor(route: Route):
        request_body = route.request.post_data_json
        updated_body = {
            **(request_body or {}),
            "insuranceCompanyId": int(resource_global_payer),
        }
        await route.continue_(
            post_data=json.dumps(updated_body), headers=route.request.headers
        )

    await page.route(API.AUTH_SETTINGS.SET_SETTING, add_payor)
    await page.get_by_role("button", name="Save", exact=True).click()

    return True


async def set_global_payer(page: Page, payer: str):
    try:
        global_auth = page.get_by_text("Global Authorization Settings")
        edit = page.locator(".pull-right > a:nth-child(2)").first
        await global_auth.first.hover()
        await edit.wait_for(state="visible")
        await edit.click()

        async def add_payor(route: Route):
            request_body = route.request.post_data_json
            updated_body = {**(request_body or {}), "authContactPayorId": int(payer)}
            await route.continue_(
                post_data=json.dumps(updated_body), headers=route.request.headers
            )

        await page.route(API.AUTH_SETTINGS.SET_GLOBAL_SETTING, add_payor)
        await page.get_by_role("button", name="Save Changes", exact=True).click()
        return True
    except Exception as e:
        logger.error(e)
        return False
