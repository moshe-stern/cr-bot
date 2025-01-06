import dataclasses
from datetime import date


@dataclasses.dataclass
class Authorization:
    ServiceCodeId: int
    authorizationId: int


@dataclasses.dataclass
class AuthSetting:
    Id: int
    Authorizations: list[Authorization]


@dataclasses.dataclass()
class AuthorizationSettingPayload:
    resourceId: int
    insuranceCompanyId: int
    authorizationSettingId: int
    frequency: str
    endDate: str
    startDate: str


@dataclasses.dataclass
class Billing:
    Id: int
    DateOfService: date
    ClientId: int
    ProviderId: int
    ProcedureCodeString: str
