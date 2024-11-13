import dataclasses
from dataclasses import dataclass
from typing import List, Callable, Union, TypeVar
from enum import Enum
from playwright.sync_api import Page

T = TypeVar("T", bound="CRResource")


class UpdateType(Enum):
    CODES = "codes"
    PAYORS = "payors"


class CRResource:
    resource_id: int
    update: Callable[[Page, T], List[bool]]

    def __init__(self, resource_id: int, update: Callable[[Page, T], List[bool]]):
        self.resource_id = resource_id
        self.update = update


class CRCodeResource(CRResource):
    to_remove: List[str] = []
    to_add: List[str] = []

    def __init__(
        self,
        resource_id: int,
        update: Callable[[Page, "CRCodeResource"], List[bool]],
        to_remove: List[str] = None,
        to_add: List[str] = None,
    ):
        super().__init__(resource_id, update)
        self.to_remove = to_remove if to_remove is not None else []
        self.to_add = to_add if to_add is not None else []


class CRPayerResource(CRResource):
    global_payer: str

    def __init__(
        self,
        resource_id: int,
        update: Callable[[Page, "CRPayerResource"], List[bool]],
        global_payer: str,
    ):
        super().__init__(resource_id, update)
        self.global_payer = global_payer
