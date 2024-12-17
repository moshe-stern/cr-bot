import dataclasses
import datetime
from enum import Enum
from typing import Tuple


class UpdateType(Enum):
    CODES = "Service Codes"
    PAYORS = "Payors"
    SCHEDULE = "Schedules"
    BILLING = "Billing"


class UpdateKeys:
    pass


@dataclasses.dataclass
class CRResource:
    id: int
    update_type: UpdateType
    updates: UpdateKeys


@dataclasses.dataclass
class ServiceCodeUpdateKeys(UpdateKeys):
    to_add: list[str]
    to_remove: list[str]


@dataclasses.dataclass
class ScheduleUpdateKeys(UpdateKeys):
    codes: list[str]


@dataclasses.dataclass
class PayorUpdateKeys(UpdateKeys):
    global_payer: str


@dataclasses.dataclass
class BillingUpdateKeys(UpdateKeys):
    start_date: str
    end_date: str
    insurance_id: int
    authorization_name: str
    place_of_service: str
    service_address: str
