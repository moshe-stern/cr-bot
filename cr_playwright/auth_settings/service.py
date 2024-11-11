import os
import logging
from typing import List
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page
from cr.actions import load_auth_settings, get_service_codes
from cr.api import  API
from cr.org import kadiant
from cr.session import CRSession
from cr_playwright.auth_settings.resources import CRResource
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
if os.getenv('DEVELOPMENT') and not load_dotenv():
    raise Exception('could not import env file')
cr_session = None

def playwright_update_auth_settings(resources_to_update: List[CRResource]):
     with sync_playwright() as p:
        global cr_session
        updated_resources = {
            resource.id: [False, False] for resource in resources_to_update
        }
        print('hi')
        logger.info('hi')
        print(os.getenv('CR_API_KEY_KADIANT_HOME'))
        logger.info(os.getenv('CR_API_KEY_KADIANT_HOME'))
        cr_session = CRSession(kadiant)
        browser =  p.chromium.launch(headless=not os.getenv('DEVELOPMENT'))
        page =  browser.new_page()
        page.goto(
        "https://login.centralreach.com/login"
        )
        log_in(page)
        for resource in resources_to_update:
            try:
                authorization_page = f'https://members.centralreach.com/#resources/details/?id={resource.id}&tab=authorizations'
                goto_auth_settings(page, authorization_page)
                auth_settings = load_auth_settings(cr_session, resource.id)
                for auth_setting in auth_settings:
                    group = page.locator(f'#group-auth-{auth_setting['Id']}')
                    group.wait_for(state="visible")
                    group.hover()
                    edit = group.locator('a').nth(1)
                    edit.wait_for(state="visible")
                    edit.click()
                    print('Updating codes for:', auth_setting['Id'])
                    page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
                    updated_settings = update_auth_setting(page, resource.codes_to_add, resource.codes_to_remove)
                    updated_resources[resource.id] = updated_settings
            except Exception as e:
                print(f"Failed to update resource {resource.id}: {e}")
        browser.close()
        print('Finished')
        return updated_resources


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
    if page.url != authorization_page or page.locator("text=Resource Not Found").is_visible():
        raise Exception('Resource does not exist')
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
    updated_codes = [0,0]
    for code in codes_add:
        if len(get_service_codes(cr_session, code)) == 0:
            print('Code not found:', code)
            continue
        has_code = page.locator("#service-codes div").get_by_text(code, exact=True)
        if has_code.is_visible():
            print('Has code:', code)
            continue
        add = page.get_by_role("link", name="Add service code")
        add.click()
        search = page.locator('.select2-input.select2-focused')
        search.fill(code)
        page.expect_response(API.SERVICE_CODES.GET)
        page.keyboard.press('Enter')
        updated_codes[0] += 1
        print('Adding code:', code)
    for code in codes_remove:
        remove = page.locator("#service-codes div").get_by_text(code, exact=True)
        is_remove = remove.is_visible()
        if is_remove:
            remove.click()
            delete_button = page.get_by_role("button", name="Yes", exact=True)
            delete_button.wait_for(state="visible")
            delete_button.click()
            updated_codes[1] += 1
            print('Deleted:', code)
        else:
            print('Code not found:', code)
    page.get_by_role("button", name="Save", exact=True).click()
    return [updated_codes[0] == len(codes_add), updated_codes[1] == len(codes_remove)]
