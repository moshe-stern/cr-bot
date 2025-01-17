import os
from typing import Union

from playwright.async_api import Playwright

from src.classes import AIOHTTPClientSession, CRSession, orgs

_cr_session: Union[CRSession, None] = None


async def start(instance: str):
    global _cr_session
    cr_instance = orgs[instance]
    if not cr_instance:
        raise Exception("Invalid cr instance")
    _cr_session = CRSession(cr_instance)


async def start_with_playwright(p: Playwright, instance: str):
    global _cr_session
    browser = await p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
    cr_instance = orgs[instance]
    if not cr_instance:
        raise Exception("Invalid cr instance")
    context = await browser.new_context()
    _cr_session = CRSession(cr_instance, context.request)
    return context


async def get_cr_session():
    if not _cr_session:
        raise Exception("cr_session not initialized")
    await _cr_session.make_context_cookies()
    return _cr_session
