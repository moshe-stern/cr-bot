import os
from typing import Union, Sequence
from playwright.async_api import Playwright

from src.actions.playwright_make_cookies import playwright_make_cookies
from src.modules.shared.world import World
from src.org import orgs
from src.session import CRSession


async def start(p: Playwright, instance: str):
    browser = await p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
    cr_instance = orgs[instance]
    if not cr_instance:
        raise Exception("Invalid cr instance")
    cr_session = CRSession(cr_instance)
    context = await browser.new_context()
    req = context.request
    await playwright_make_cookies(req, cr_session.cr_token_response.access_token)
    return {"session": cr_session, "context": context}
