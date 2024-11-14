import os
from typing import Union
from playwright.sync_api import sync_playwright, Playwright
from src.modules.shared.world import World
from src.org import orgs
from src.session import CRSession

world: Union[World, None] = None


def start(p: Playwright, instance: str):
    global world
    browser = p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
    page = browser.new_page()
    cr_instance = orgs[instance]
    if not cr_instance:
        raise Exception("Invalid cr instance")
    world = World(page, CRSession(cr_instance), browser)


def get_world() -> World:
    if world is None:
        raise Exception("World isn't initialized")
    return world
