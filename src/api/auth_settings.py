from src.api import API
from src.api.index import do_cr_post
from src.classes import CRSession, AuthSetting, AuthorizationSettingPayload


def load_auth_settings(session: CRSession, resources_id: int) -> list[dict[str, str]]:
    res = session.post(
        API.AUTH_SETTINGS.LOAD_SETTINGS,
        json={"resourceId": resources_id, "_utcOffsetMinutes": 300},
    )
    if res.ok:
        data = res.json()
        return data.get("authorizationSettings")
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


async def set_auth_setting(session: CRSession, payload: AuthorizationSettingPayload):
    res = await do_cr_post(
        API.AUTH_SETTINGS.SET_SETTING,
        {
            "resourceId": payload.resourceId,
            "insuranceCompanyId": payload.insuranceCompanyId,
            "authorizationSettingId": payload.authorizationSettingId,
            "frequency": payload.frequency,
            "endDate": payload.endDate,
            "startDate": payload.startDate,
        },
        session,
    )
    data = {"success": False}
    if res.ok:
        data = await res.json()
    return {
        "resource": payload.resourceId,
        "setting": payload.authorizationSettingId,
        "updated": data["success"],
    }


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
