import os
from typing import Union, Sequence
from playwright.async_api import Playwright

from src.actions.playwright_make_cookies import playwright_make_cookies
from src.modules.shared.world import World
from src.org import orgs
from src.session import CRSession

_cr_session: Union[CRSession, None] = None


async def start(p: Playwright, instance: str):
    global _cr_session
    browser = await p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
    cr_instance = orgs[instance]
    if not cr_instance:
        raise Exception("Invalid cr instance")
    _cr_session = CRSession(cr_instance)
    context = await browser.new_context()
    req = context.request
    await playwright_make_cookies(req, _cr_session.cr_token_response.access_token)
    return context


def get_cr_session() -> CRSession:
    if not _cr_session:
        raise Exception("cr_session not initialized")
    return _cr_session
