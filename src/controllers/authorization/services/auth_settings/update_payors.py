from playwright.async_api import Page

from src.classes import CRPayerResource

global_payer = None


async def update_payors(payor_resource: CRPayerResource, page: Page):
    combo = page.get_by_role("combobox")
    await combo.click()
    await combo.select_option(payor_resource.global_payer)
    await page.keyboard.press("Enter")
    await page.get_by_role("button", name="Save", exact=True).click()
    if not global_payer:
        await set_global_payer(page, payor_resource.global_payer)
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
