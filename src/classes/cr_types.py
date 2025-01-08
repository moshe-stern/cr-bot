import dataclasses


@dataclasses.dataclass
class Authorization:
    service_code_id: int
    id: int


@dataclasses.dataclass
class AuthSetting:
    id: int
    authorizations: list[Authorization]


@dataclasses.dataclass
class Billing:
    id: int
    date_of_service: str
    provider_id: int
    procedure_code_string: str


@dataclasses.dataclass
class AuthorizationData:
    authorizationNumber: str
    billingId: int
    clientAcceptedHoursFrequency: str
    endDate: str
    firstDayOfWeek: int
    frequency: str
    id: int
    insuranceCompanyId: int
    organizationId: int
    providerSupplierId: int
    referrerId: int
    resourceId: int
    startDate: str
