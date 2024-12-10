from playwright.async_api import BrowserContext

from src.classes.session import CRSession


class World:
    def __init__(
        self,
        context: BrowserContext,
        cr_session: CRSession,
    ):
        self.context = context
        self.cr_session = cr_session
