import os
from typing import Union, Sequence
from playwright.sync_api import sync_playwright, Playwright

from src.actions.playwright_make_cookies import playwright_make_cookies
from src.modules.shared.world import World
from src.org import orgs
from src.session import CRSession

world: Union[World, None] = None


def start(p: Playwright, instance: str):
    global world
    browser = p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
    cr_instance = orgs[instance]
    if not cr_instance:
        raise Exception("Invalid cr instance")
    cr_session = CRSession(cr_instance)
    context = browser.new_context()
    req = context.request
    playwright_make_cookies(req, cr_session.cr_token_response.access_token)
    world = World(context, cr_session)


def get_world() -> World:
    if world is None:
        raise Exception("World isn't initialized")
    return world
