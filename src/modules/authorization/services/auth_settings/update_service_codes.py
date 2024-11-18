import time

from src.actions.auth_settings import get_service_codes
from src.api import API
from src.modules.shared.start import get_world
from src.resources import CRCodeResource


def update_service_codes(code_resource: CRCodeResource) -> bool:
    world = get_world()
    page = world.page
    cr_session = world.cr_session
    service_codes = page.get_by_role("link", name="Service Code(s)")
    service_codes.wait_for(state="visible")
    service_codes.click()
    updated_codes = [0, 0]
    for code in code_resource.to_add:
        if len(get_service_codes(cr_session, code)) == 0:
            continue
        has_code = page.locator("#service-codes div").get_by_text(code, exact=True)
        if has_code.is_visible():
            continue
        add = page.get_by_role("link", name="Add service code")
        add.click()
        search = page.locator(".select2-input.select2-focused")
        search.fill(code)
        page.expect_response(API.SERVICE_CODES.GET)
        time.sleep(2)
        page.keyboard.press("Enter")
        updated_codes[0] += 1
    for code in code_resource.to_remove:
        remove = page.locator(".list-group-item").get_by_text(code, exact=True)
        is_remove = remove.is_visible()
        if is_remove:
            remove.locator("~ a").click()
            delete_button = page.get_by_role("button", name="Yes", exact=True)
            delete_button.wait_for(state="visible")
            delete_button.click()
            updated_codes[1] += 1
    page.get_by_role("button", name="Save", exact=True).click()
    return updated_codes[0] == len(code_resource.to_add) and updated_codes[1] == len(
        code_resource.to_remove
    )
