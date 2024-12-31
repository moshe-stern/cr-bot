import dataclasses


@dataclasses.dataclass
class Authorization:
    ServiceCodeId: int
    authorizationId: int


@dataclasses.dataclass
class AuthSetting:
    Id: int
    Authorizations: list[Authorization]
