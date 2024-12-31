from src.api import API
from src.api.index import do_cr_post
from src.classes import CRSession, AuthSetting


async def load_auth_settings(
    session: CRSession, resources_id: int
) -> list[AuthSetting]:
    res = await do_cr_post(
        API.AUTH_SETTINGS.LOAD_SETTINGS,
        {"resourceId": resources_id, "_utcOffsetMinutes": 300},
        session,
    )
    if res.ok:
        data = await res.json()
        return data["authorizationSettings"]
    else:
        return []

def load_auth_setting(session: CRSession, authorization_setting_id: int):
    return session.post(
        API.AUTH_SETTINGS.SET_SETTING,
        json={
            "authorizationSettingId": authorization_setting_id,
            "_utcOffsetMinutes": 300,
        },
    ).json()


def set_auth_setting(session: CRSession, service_code: int, setting_id: int):
    return session.post(
        API.AUTH_SETTINGS.SET_SETTING,
        json={"serviceCodeId": service_code, "settingsId": setting_id},
    )


async def get_service_codes(session: CRSession, code: str) -> list[int]:
    response = await do_cr_post(
        API.SERVICE_CODES.GET,
        {"search": code, "searchTerm": code, "_utcOffsetMinutes": 300},
        session,
    )
    if response.ok:
        data = await response.json()
        return [item["Id"] for item in data["codes"]]
    else:
        return []
