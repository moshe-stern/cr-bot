from playwright.sync_api import Page, Browser, Playwright

from src.session import CRSession


class World:
    def __init__(
        self,
        page: Page,
        cr_session: CRSession,
        browser: Browser,
    ):
        self.page = page
        self.cr_session = cr_session
        self.browser = browser

    def close(self):
        self.page.close()
        self.browser.close()
