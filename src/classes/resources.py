import dataclasses
from dataclasses import dataclass
from typing import List, Callable, Union, TypeVar, Awaitable
from enum import Enum

from playwright.async_api import Page

T = TypeVar("T", bound="CRResource")


class UpdateType(Enum):
    CODES = "Service Codes"
    PAYORS = "Payors"
    SCHEDULE = "Schedules"


class CRResource:
    resource_id: int
    update: Callable[[T, Page], Awaitable[bool | None]]

    def __init__(
        self, resource_id: int, update: Callable[[T, Page], Awaitable[bool | None]]
    ):
        self.resource_id = resource_id
        self.update = update


class CRCodeResource(CRResource):
    to_remove: List[str] = []
    to_add: List[str] = []

    def __init__(
        self,
        resource_id: int,
        update: Callable[["CRCodeResource", Page], Awaitable[bool | None]],
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
        update: Callable[["CRPayerResource", Page], Awaitable[bool | None]],
        global_payer: str,
    ):
        super().__init__(resource_id, update)
        self.global_payer = global_payer


class CRScheduleResource:
    def __init__(
        self,
        client_id: int,
        codes: List[str],
    ):
        self.client_id = client_id
        self.codes = codes
