import dataclasses


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
