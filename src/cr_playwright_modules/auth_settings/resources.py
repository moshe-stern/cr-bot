import dataclasses
from typing import List
import enum

from src.cr_playwright_modules.auth_settings.services.payors import update_payors
from src.cr_playwright_modules.auth_settings.services.service_codes import (
    update_service_codes,
)


class UpdateType(enum):
    CODES = "codes"
    PAYERS = "payers"


@dataclasses.dataclass
class CRResource:
    id: int
    to_remove: List[str]
    to_add: List[str]


update_functions = {
    UpdateType.CODES: update_service_codes,
    UpdateType.PAYERS: update_payors,
}
# test_resource = Resource(
#     50704127,
#     ['97151: ASMT/Reassessment', '97151: Assessment, Lic/Cert only - REVIEWER'],
#     ['97152: Additional Assessment by BCBA']
# )
# resources_to_update = [test_resource]
