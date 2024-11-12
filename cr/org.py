from dataclasses import dataclass


class CR_Org_Type:
    Home = 'HOME'
    School = 'school'


@dataclass
class CR_Org:
    organizationId: int
    cr_name: str
    org_type: CR_Org_Type
    org_str: str


kadiant = CR_Org(427999, 'kadiantadmin', CR_Org_Type.Home, 'KADIANT')
attain = CR_Org(1098187, 'brightadmin', CR_Org_Type.Home, 'attain')
