from playwright.sync_api import Page

from src.modules.shared.start import get_world
from src.resources import CRPayerResource

global_payer = None


def update_payors(payor_resource: CRPayerResource, page: Page):
    combo = page.get_by_role("combobox")
    combo.click()
    combo.select_option(payor_resource.global_payer)
    page.keyboard.press("Enter")
    page.get_by_role("button", name="Save", exact=True).click()
    if not global_payer:
        set_global_payer(page, payor_resource.global_payer)
    return True


def set_global_payer(page: Page, payer: str):
    global global_payer
    global_payer = payer
    global_auth = page.get_by_text("Global Authorization Settings")
    edit = page.locator(".pull-right > a:nth-child(2)").first
    global_auth.hover()
    edit.wait_for(state="visible")
    edit.click()
    combo = page.get_by_role("combobox").first
    combo.wait_for(state="visible")
    combo.click()
    combo.select_option(global_payer)
    page.keyboard.press("Enter")
    page.get_by_role("button", name="Save Changes").click()
