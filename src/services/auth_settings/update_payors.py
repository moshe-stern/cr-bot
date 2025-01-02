import time
from typing import cast

from playwright.async_api import Page
from src.classes import CRResource, PayorUpdateKeys
from src.shared import logger



async def update_payors(payor_resource: CRResource, page: Page):
    resource_global_payer = cast(PayorUpdateKeys, payor_resource.updates).global_payor
    combo = page.get_by_role("combobox")
    await combo.click()
    options = await combo.get_by_role("option").all_text_contents()
    index = options.index(resource_global_payer)
    await combo.select_option(index=index, timeout=1000)
    await page.keyboard.press("Enter")
    await page.get_by_role("button", name="Save", exact=True).click()
    return True


async def set_global_payer(page: Page, payer: str):
    global_auth = page.get_by_text("Global Authorization Settings")
    edit = page.locator(".pull-right > a:nth-child(2)").first
    await global_auth.first.hover()
    await edit.wait_for(state="visible")
    await edit.click()
    combo = page.get_by_role("combobox").first
    await combo.wait_for(state="visible")
    await combo.click()
    options = await combo.get_by_role("option").all_text_contents()
    index = options.index(payer)
    await combo.select_option(index=index, timeout=1000)
    await page.keyboard.press("Enter")
    await page.get_by_role("button", name="Save Changes").click()
