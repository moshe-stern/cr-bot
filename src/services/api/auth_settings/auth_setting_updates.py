from dacite import from_dict

from src.classes import (API, AIOHTTPClientSession, Authorization, AuthSetting,
                         CRResource)


async def get_auth_settings_updates(
    client: AIOHTTPClientSession, resource_id: int, updates: dict
):
    res = await client.do_cr_fetch(
        API.AUTH_SETTINGS.LOAD_SETTINGS,
        {"resourceId": int(resource_id), "_utcOffsetMinutes": 300},
    )
    if res.ok:
        data = await res.json()
        settings = [
            from_dict(
                data_class=AuthSetting,
                data={
                    "id": auth_setting["Id"],
                    "authorizations": [
                        from_dict(
                            data_class=Authorization,
                            data={
                                "service_code_id": auth.get("ServiceCodeId"),
                                "id": auth.get("Id"),
                            },
                        )
                        for auth in auth_setting.get("Authorizations", [])
                    ],
                },
            )
            for auth_setting in data.get("authorizationSettings", [])
        ]
        return {resource_id: {"settings": settings, **updates}}
    else:
        return {resource_id: {"settings": [], **updates}}
