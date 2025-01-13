from dacite import from_dict

from src.classes import API, AIOHTTPClientSession, AuthSetting, CRSession, cr_types


async def load_auth_settings(
    client: AIOHTTPClientSession, resources_id: int
) -> list[AuthSetting]:
    res = await client.do_cr_fetch(
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


async def load_auth_setting(client: AIOHTTPClientSession, setting_id: int):
    res = await client.do_cr_fetch(
        API.AUTH_SETTINGS.LOAD_SETTING,
        {
            "authorizationSettingId": setting_id,
            "_utcOffsetMinutes": 300,
        },
    )

    def convert_obj_keys_to_lower(obj: dict):
        return {key[0].lower() + key[1:]: value for key, value in obj.items()}

    if res.ok:
        data = await res.json()
        return {
            **convert_obj_keys_to_lower(data.get("authorizationSetting")),
            "diagnosisCodes": [
                {
                    "code": str(code.get("Code")),
                    "description": code.get("Description"),
                    "id": code.get("Id"),
                    "name": code.get("name"),
                    "pointer": "",
                    "version": code.get("Version"),
                }
                for code in data.get("diagnosisCodes", [])
            ],
            "authorizations": [
                convert_obj_keys_to_lower(auth)
                for auth in data.get("authorizations", [])
            ],
        }


async def set_auth_setting(
    client: AIOHTTPClientSession, setting_id: int, global_payor: int
):
    loaded_setting = await load_auth_setting(client, setting_id)
    if not loaded_setting:
        return False
    res = await client.do_cr_fetch(
        API.AUTH_SETTINGS.SET_SETTING,
        {
            **loaded_setting,
            "insuranceCompanyId": global_payor,
            "authorizationSettingId": loaded_setting.get("id"),
            "diagnosisString": ",".join(
                [
                    str(code.get("id"))
                    for code in loaded_setting.get("diagnosisCodes", [])
                ]
            ),
        },
    )
    if res.ok:
        data = await res.json()
        return data["success"]
    else:
        return False


async def get_service_codes(client: AIOHTTPClientSession, code: str) -> list[int]:
    response = await client.do_cr_fetch(
        API.SERVICE_CODES.GET,
        {"search": code, "searchTerm": code, "_utcOffsetMinutes": 300},
    )
    if response.ok:
        data = await response.json()
        return [item["Id"] for item in data["codes"]]
    else:
        return []
