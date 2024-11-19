import time

from playwright.async_api import Page

from src.api import API


async def log_in(page: Page):
    await page.goto("https://login.centralreach.com/login")
    email = page.get_by_placeholder("Email address")
    await email.wait_for(state="visible")
    await email.fill("kadiant.automate@kadiant.com")
    await page.get_by_role("button", name="Next").click()
    password = page.get_by_placeholder("Password")
    await password.wait_for(state="visible")
    await password.click()
    await password.fill("R##oGq@M%soGblD25FQB2u7*e")
    await page.get_by_role("button", name="Log in").click()
    cr_instance = page.get_by_test_id("ent-prod|kadiantadmin")
    await cr_instance.wait_for(state="visible")
    await cr_instance.click()
    await check_for_multiple_login(page)


async def check_for_multiple_login(page: Page):
    home = page.get_by_text(
        "HomeContactsFilesBillingClaimsHRSchedulingClinicalInsightsKADIANT LLC"
    )
    await home.wait_for(state="visible")
    await page.wait_for_load_state("domcontentloaded")
    page.expect_response(API.SERVICE_CODES.GET_PLACES_OF_SERVICE)
    time.sleep(2)
    continue_to_login = page.get_by_role("button", name="Continue To Login")
    is_visible = await continue_to_login.is_visible()
    if is_visible:
        await continue_to_login.click()
