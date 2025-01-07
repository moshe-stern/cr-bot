import dataclasses
import datetime
from enum import Enum
from typing import Tuple

from pandas import Series


class UpdateType(Enum):
    CODES = "Service Codes"
    PAYORS = "Payors"
    SCHEDULE = "Schedules"
    BILLING = "Billing"
    TIMESHEET = "Time Sheet"


class UpdateKeys:
    pass


@dataclasses.dataclass
class CRResource:
    id: int
    update_type: UpdateType
    updates: UpdateKeys

    def __init__(self, update_type: UpdateType, updates: UpdateKeys, **kwargs) -> None:
        self.id = kwargs.get("id", 0)
        self.updates = updates
        self.update_type = update_type


class ServiceCodeUpdateKeys(UpdateKeys):
    to_add: list[str]
    to_remove: list[str]

    def __init__(self, **kwargs) -> None:
        self.to_add = kwargs.get("to_add", [])
        self.to_remove = kwargs.get("to_remove", [])


class ScheduleUpdateKeys(UpdateKeys):
    codes: list[str]

    def __init__(self, **kwargs) -> None:
        self.codes = kwargs.get("codes", [])


class PayorUpdateKeys(UpdateKeys):
    global_payor: str

    def __init__(self, **kwargs) -> None:
        self.global_payor = kwargs.get("global_payor", "")


class BillingUpdateKeys(UpdateKeys):
    start_date: str
    end_date: str
    insurance_id: int

    def __init__(self, **kwargs) -> None:
        self.start_date = kwargs.get("start_date", "")
        self.end_date = kwargs.get("end_date", "")
        self.insurance_id = kwargs.get("insurance_id", 0)


class TimeSheetUpdateKeys(UpdateKeys):
    start_date: str
    end_date: str
    insurance_id: int

    def __init__(self, **kwargs) -> None:
        self.start_date = kwargs.get("start_date", "")
        self.end_date = kwargs.get("end_date", "")
        self.insurance_id = kwargs.get("insurance_id", 0)
