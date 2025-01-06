import dataclasses


@dataclasses.dataclass
class Authorization:
    service_code_id: int
    authorization_id: int


@dataclasses.dataclass
class AuthSetting:
    id: int
    authorizations: list[Authorization]


@dataclasses.dataclass()
class AuthorizationSettingPayload:
    resource_id: int
    insurance_company_id: int
    authorization_setting_id: int
    frequency: str
    end_date: str
    start_date: str


@dataclasses.dataclass
class Billing:
    id: int
    date_of_service: str
    provider_id: int
    procedure_code_string: str
