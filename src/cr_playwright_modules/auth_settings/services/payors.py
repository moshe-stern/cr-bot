from playwright.sync_api import Page

from src.cr_playwright_modules.auth_settings.resources import CRPayerResource


def update_payors(page: Page, payor_resource: CRPayerResource):
    combo = page.get_by_role("combobox")
    combo.fill(payor_resource.global_payer)
    page.get_by_role("button", name="Save Changes").click()


def set_global_payer(page: Page, global_payer: str):
    page.locator(".pull-right > a:nth-child(2)").first.click()
    global_auth = page.get_by_role("link", name="Global Authorization Settings")
    global_auth.wait_for(state="visible")
    combo = page.get_by_role("combobox").first
    combo.click()
    combo.fill(global_payer)
    page.get_by_role("button", name="Save Changes").click()
