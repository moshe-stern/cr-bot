import os
from typing import Union
from playwright.sync_api import sync_playwright, Playwright
from src.modules.shared.world import World
from src.org import kadiant
from src.session import CRSession

world: Union[World, None] = None


def start(p: Playwright):
    global world
    browser = p.chromium.launch(headless=not os.getenv("DEVELOPMENT"))
    page = browser.new_page()
    world = World(page, CRSession(kadiant), browser)


def get_world() -> World:
    return world
