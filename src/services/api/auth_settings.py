from src.classes import (
    CRSession,
    AuthSetting,
    AuthorizationSettingPayload,
    AIOHTTPClientSession,
    cr_types,
    API,
)


async def load_auth_settings(
    client: AIOHTTPClientSession, resources_id: int
) -> list[AuthSetting]:
    res = await client.do_cr_post(
        API.AUTH_SETTINGS.LOAD_SETTINGS,
        {"resourceId": resources_id, "_utcOffsetMinutes": 300},
    )
    if res.ok:
        data = await res.json()
        settings: list[AuthSetting] = [
            AuthSetting(
                auth_setting["Id"],
                [
                    cr_types.Authorization(auth.get("ServiceCodeId"), auth.get("Id"))
                    for auth in auth_setting.get("Authorizations")
                ],
            )
            for auth_setting in data.get("authorizationSettings")
        ]
        return settings
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


async def set_auth_setting(
    client: AIOHTTPClientSession, payload: AuthorizationSettingPayload
):
    res = await client.do_cr_post(
        API.AUTH_SETTINGS.SET_SETTING,
        {
            "resourceId": payload.resourceId,
            "insuranceCompanyId": payload.insuranceCompanyId,
            "authorizationSettingId": payload.authorizationSettingId,
            "frequency": payload.frequency,
            "endDate": payload.endDate,
            "startDate": payload.startDate,
        },
    )
    data = {"success": False}
    if res.ok:
        data = await res.json()
    return {
        "resource": payload.resourceId,
        "setting": payload.authorizationSettingId,
        "updated": data["success"],
    }


async def get_service_codes(client: AIOHTTPClientSession, code: str) -> list[int]:
    response = await client.do_cr_post(
        API.SERVICE_CODES.GET,
        {"search": code, "searchTerm": code, "_utcOffsetMinutes": 300},
    )
    if response.ok:
        data = await response.json()
        return [item["Id"] for item in data["codes"]]
    else:
        return []
