from dataclasses import dataclass


@dataclass
class CrORG:
    organizationId: int
    cr_name: str
    org_type: str
    org_str: str


orgs = {
    "Kadiant": CrORG(427999, "kadiantadmin", "HOME", "KADIANT"),
    "Attain TSS": CrORG(1098187, "brightadmin", "HOME", "ATTAIN"),
}
