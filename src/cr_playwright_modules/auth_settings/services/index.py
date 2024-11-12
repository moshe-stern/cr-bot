import os
from typing import List
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page
from src.cr.actions import load_auth_settings
from src.cr.api import API
from src.cr.org import kadiant
from src.cr.session import CRSession
from src.cr_playwright_modules.auth_settings.resources import CRResource

if os.getenv("DEVELOPMENT") and not load_dotenv():
    raise Exception("could not import env file")
cr_session = None


def playwright_update_auth_settings(resources_to_update: List[CRResource]):
    with sync_playwright() as p:
        global cr_session
        updated_resources = {
            resource.resource_id: [False, False] for resource in resources_to_update
        }
        cr_session = CRSession(kadiant)
        browser = p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
        page = browser.new_page()
        page.goto("https://login.centralreach.com/login")
        log_in(page)
        for resource in resources_to_update:
            try:
                authorization_page = f"https://members.centralreach.com/#resources/details/?id={resource.resource_id}&tab=authorizations"
                goto_auth_settings(page, authorization_page)
                auth_settings = load_auth_settings(cr_session, resource.resource_id)
                for auth_setting in auth_settings:
                    group = page.locator(f"#group-auth-{auth_setting['Id']}")
                    group.wait_for(state="visible")
                    group.hover()
                    edit = group.locator("a").nth(1)
                    edit.wait_for(state="visible")
                    edit.click()
                    print("Updating codes for:", auth_setting["Id"])
                    page.expect_response(API.AUTH_SETTINGS.LOAD_SETTING)
                    updated_settings = resource.update(page, resource)
                    updated_resources[resource.resource_id] = updated_settings
            except Exception as e:
                print(f"Failed to update resource {resource.resource_id}: {e}")
        browser.close()
        print("Finished")
        return updated_resources


def log_in(page: Page):
    print("Log in")
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
    print("Navigate to main page")
    page.goto(authorization_page)
    if (
        page.url != authorization_page
        or page.locator("text=Resource Not Found").is_visible()
    ):
        raise Exception("Resource does not exist")
    home = page.get_by_text(
        "HomeContactsFilesBillingClaimsHRSchedulingClinicalInsightsKADIANT LLC"
    )
    home.wait_for(state="visible")
    page.wait_for_load_state("domcontentloaded")
    continue_to_login = page.get_by_role("button", name="Continue To Login")
    is_visible = continue_to_login.is_visible()
    if is_visible:
        continue_to_login.click()
