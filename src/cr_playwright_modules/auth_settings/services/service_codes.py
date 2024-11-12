from playwright.sync_api import Page

from src.cr.actions import get_service_codes
from src.cr.api import API
from src.cr_playwright_modules.auth_settings.services.index import cr_session


def update_service_codes(page: Page, codes_to_add, codes_to_remove):
    service_codes = page.get_by_role("link", name="Service Code(s)")
    service_codes.wait_for(state="visible")
    service_codes.click()
    updated_codes = [0, 0]
    for code in codes_to_add:
        if len(get_service_codes(cr_session, code)) == 0:
            print("Code not found:", code)
            continue
        has_code = page.locator("#service-codes div").get_by_text(code, exact=True)
        if has_code.is_visible():
            print("Has code:", code)
            continue
        add = page.get_by_role("link", name="Add service code")
        add.click()
        search = page.locator(".select2-input.select2-focused")
        search.fill(code)
        page.expect_response(API.SERVICE_CODES.GET)
        page.keyboard.press("Enter")
        updated_codes[0] += 1
        print("Adding code:", code)
    for code in codes_to_remove:
        remove = page.locator("#service-codes div").get_by_text(code, exact=True)
        is_remove = remove.is_visible()
        if is_remove:
            remove.click()
            delete_button = page.get_by_role("button", name="Yes", exact=True)
            delete_button.wait_for(state="visible")
            delete_button.click()
            updated_codes[1] += 1
            print("Deleted:", code)
        else:
            print("Code not found:", code)
    page.get_by_role("button", name="Save", exact=True).click()
    return [
        updated_codes[0] == len(codes_to_add),
        updated_codes[1] == len(codes_to_remove),
    ]
