from dataclasses import dataclass

from enum import Enum


class CrORGType(Enum):
    HOME = "HOME"
    SCHOOL = "SCHOOL"


class CrORGStr(Enum):
    KADIANT = "KADIANT"
    ATTAIN = "ATTAIN"


@dataclass
class CrORG:
    organizationId: int
    cr_name: str
    org_type: str
    org_str: str


orgs: dict[str, CrORG] = {
    "Kadiant": CrORG(
        427999, "kadiantadmin", CrORGType.HOME.value, CrORGStr.KADIANT.value
    ),
    "Attain TSS": CrORG(
        1098187, "brightadmin", CrORGType.HOME.value, CrORGStr.ATTAIN.value
    ),
}
