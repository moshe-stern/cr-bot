from playwright.async_api import Page


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


async def handle_dialogs(page: Page, remove: bool = False):
    async def handler():
        okay_got_it = page.get_by_role("button", name="Okay, Got It")
        continue_to_login = page.get_by_role("button", name="Continue To Login")
        close_button = page.locator('button[aria-label="Close"]')
        if await okay_got_it.is_visible():
            await okay_got_it.click()
        if await continue_to_login.is_visible():
            await continue_to_login.click()
        if await close_button.is_visible():
            await close_button.click()
    if remove:
        await page.remove_locator_handler(page.get_by_role("dialog"))
    else:
        await page.add_locator_handler(page.get_by_role("dialog"), handler)
