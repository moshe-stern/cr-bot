from typing import cast

from playwright.async_api import Page

from src.classes import CRResource, PayorUpdateKeys

global_payer = None


async def update_payors(payor_resource: CRResource, page: Page):
    resource_global_payer = cast(PayorUpdateKeys, payor_resource.updates).global_payer
    combo = page.get_by_role("combobox")
    await combo.click()
    await combo.select_option()
    await page.keyboard.press("Enter")
    await page.get_by_role("button", name="Save", exact=True).click()
    if not global_payer:
        await set_global_payer(page, str(resource_global_payer))
    return True


async def set_global_payer(page: Page, payer: str):
    global global_payer
    global_payer = payer
    global_auth = page.get_by_text("Global Authorization Settings")
    edit = page.locator(".pull-right > a:nth-child(2)").first
    await global_auth.first.hover()
    await edit.wait_for(state="visible")
    await edit.click()
    combo = page.get_by_role("combobox").first
    await combo.wait_for(state="visible")
    await combo.click()
    await combo.select_option(global_payer)
    await page.keyboard.press("Enter")
    await page.get_by_role("button", name="Save Changes").click()
