import dataclasses
from typing import List

@dataclasses.dataclass
class CRResource:
    id: int
    codes_to_remove: List[str]
    codes_to_add: List[str]


# test_resource = Resource(
#     50704127,
#     ['97151: ASMT/Reassessment', '97151: Assessment, Lic/Cert only - REVIEWER'],
#     ['97152: Additional Assessment by BCBA']
# )
# resources_to_update = [test_resource]
