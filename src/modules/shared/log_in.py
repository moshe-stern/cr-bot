import time

from src.api import API
from src.modules.shared.start import get_world


def log_in():
    world = get_world()
    page = world.page
    page.goto("https://login.centralreach.com/login")
    print("Logging in")
    email = page.get_by_placeholder("Email address")
    email.wait_for(state="visible")
    email.fill("kadiant.automate@kadiant.com")
    page.get_by_role("button", name="Next").click()
    password = page.get_by_placeholder("Password")
    password.wait_for(state="visible")
    password.click()
    password.fill("R##oGq@M%soGblD25FQB2u7*e")
    page.get_by_role("button", name="Log in").click()
    cr_instance = page.get_by_test_id("ent-prod|kadiantadmin")
    cr_instance.wait_for(state="visible")
    cr_instance.click()
    check_for_multiple_login()


def check_for_multiple_login():
    world = get_world()
    page = world.page
    home = page.get_by_text(
        "HomeContactsFilesBillingClaimsHRSchedulingClinicalInsightsKADIANT LLC"
    )
    home.wait_for(state="visible")
    page.wait_for_load_state("domcontentloaded")
    page.expect_response(API.SERVICE_CODES.GET_PLACES_OF_SERVICE)
    time.sleep(2)
    continue_to_login = page.get_by_role("button", name="Continue To Login")
    is_visible = continue_to_login.is_visible()
    if is_visible:
        continue_to_login.click()
