import time
from playwright.sync_api import sync_playwright, Page
from cr.actions import load_auth_settings
from cr.api import BASE_URL, API
from cr.org import kadiant
from cr.session import CRSession


def playwright_update_auth_settings():
     with sync_playwright() as p:
        codes_to_remove = ['97151: ASMT/Reassessment', '97151: Assessment, Lic/Cert only - REVIEWER']
        codes_to_add = ['97152: Additional Assessment by BCBA']
        resource_id = 50704127
        authorization_page = f'https://members.centralreach.com/#resources/details/?id={resource_id}&tab=authorizations'
        browser =  p.chromium.launch()
        page =  browser.new_page()
        page.goto(
        "https://login.centralreach.com/login"
        )
        log_in(page)
        goto_auth_settings(page, authorization_page)
        auth_settings = load_auth_settings(CRSession(kadiant), resource_id)
        for auth_setting in auth_settings:
            group = page.locator(f'#group-auth-{auth_setting['Id']}')
            group.wait_for(state="visible")
            group.hover()
            edit = group.locator('a').nth(1)
            edit.wait_for(state="visible")
            edit.click()
            print('Updating codes for:', auth_setting['Id'])
            page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
            update_auth_setting(page, codes_to_add, codes_to_remove)
        browser.close()
        print('Finished')


def log_in(page: Page):
    print('Log in')
    email = page.get_by_placeholder("Email address")
    email.wait_for(state="visible")
    email.fill("moshe.stern@attainaba.com")
    page.get_by_role("button", name="Next").click()
    password = page.get_by_placeholder("Password")
    password.wait_for(state="visible")
    password.click()
    password.fill("xrh*qep*cha-PXD1crz")
    page.get_by_role("button", name="Log in").click()
    cr_instance = page.get_by_test_id("ent-prod|kadiantadmin")
    cr_instance.wait_for(state="visible")
    cr_instance.click()


def goto_auth_settings(page: Page, authorization_page):
    print('Navigate to main page')
    page.goto(authorization_page)
    home = page.get_by_text("HomeContactsFilesBillingClaimsHRSchedulingClinicalInsightsKADIANT LLC")
    home.wait_for(state="visible")
    page.wait_for_load_state('domcontentloaded')
    continue_to_login = page.get_by_role("button", name="Continue To Login")
    is_visible =  continue_to_login.is_visible()
    if is_visible:
        continue_to_login.click()


def update_auth_setting(page: Page, codes_add, codes_remove):
    service_codes = page.get_by_role("link", name="Service Code(s)")
    service_codes.wait_for(state="visible")
    service_codes.click()
    for code in codes_add:
        has_code = page.locator("#service-codes div").get_by_text(code, exact=True)
        if has_code:
            print('Has code:', code)
            continue
        add = page.get_by_role("link", name="Add service code")
        add.click()
        search = page.locator('.select2-input.select2-focused')
        search.fill(code)
        page.expect_response(API.SERVICE_CODES.GET)
        page.keyboard.press('Enter')
        print('Adding code:', code)
    for code in codes_remove:
        remove = page.locator("#service-codes div").get_by_text(code, exact=True)
        is_remove = remove.is_visible()
        if is_remove:
            remove.click()
            delete_button = page.get_by_role("button", name="Yes", exact=True)
            delete_button.wait_for(state="visible")
            delete_button.click()
            print('Deleted:', code)
        else:
            print('Code not found:', code)
    page.get_by_role("button", name="Save", exact=True).click()
