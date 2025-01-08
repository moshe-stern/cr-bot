import time
from typing import cast

from playwright.async_api import Page

from src.classes import (API, AIOHTTPClientSession, CRResource,
                         ServiceCodeUpdateKeys)
from src.services.api import get_service_codes


async def update_service_codes(
    code_resource: CRResource, page: Page, client: AIOHTTPClientSession
) -> bool | None:
    service_code_updates = cast(ServiceCodeUpdateKeys, code_resource.updates)
    service_codes = page.get_by_role("link", name="Service Code(s)")
    await service_codes.wait_for(state="visible")
    await service_codes.click()
    updated_codes = [0, 0]
    for code in service_code_updates.to_add:
        if len(await get_service_codes(client, code)) == 0:
            continue
        updated_codes[0] += 1
        has_code = page.locator("#service-codes div").get_by_text(code, exact=True)
        if await has_code.is_visible():
            continue
        add = page.get_by_role("link", name="Add service code")
        await add.click()
        search = page.locator(".select2-input.select2-focused")
        await search.fill(code)
        page.expect_response(API.SERVICE_CODES.GET)
        time.sleep(2)
        await page.keyboard.press("Enter")
    for code in service_code_updates.to_remove:
        remove = page.locator(".list-group-item").get_by_text(code, exact=True)
        is_remove = await remove.is_visible()
        if is_remove:
            await remove.locator("~ a").click()
            delete_button = page.get_by_role("button", name="Yes", exact=True)
            await delete_button.wait_for(state="visible")
            await delete_button.click()
        updated_codes[1] += 1
    await page.get_by_role("button", name="Save", exact=True).click()
    updated: bool | None = (
        updated_codes[0] == len(service_code_updates.to_add)
        and updated_codes[1] == len(service_code_updates.to_remove)
        or None
    )
    return updated
