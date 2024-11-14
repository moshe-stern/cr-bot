from dataclasses import dataclass


@dataclass
class CrORG:
    organizationId: int
    cr_name: str
    org_type: str
    org_str: str


orgs = {
    "kadiant": CrORG(427999, "kadiantadmin", "HOME", "KADIANT"),
    "attain": CrORG(1098187, "brightadmin", "HOME", "ATTAIN"),
}
