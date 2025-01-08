import asyncio

from src.classes import API, AIOHTTPClientSession, Authorization, AuthSetting


async def set_authorization_in_setting(
    client: AIOHTTPClientSession,
    setting: AuthSetting,
    service_code_id: int,
):
    if next(
        (auth.service_code_id == service_code_id for auth in setting.authorizations),
        False,
    ):
        return True
    res = await client.do_cr_fetch(
        API.AUTHORIZATION.SET,
        {
            "serviceCodeId": service_code_id,
            "settingsId": setting.id,
        },
    )
    if res.ok:
        data = await res.json()
        return data.get("success")
    else:
        return False


async def delete_authorizations_in_setting(
    client: AIOHTTPClientSession,
    setting: AuthSetting,
    service_code_id: int,
):
    auths_to_delete = [
        auth
        for auth in setting.authorizations
        if auth.service_code_id == service_code_id
    ]
    if not auths_to_delete:
        return True

    async def delete_authorization(auth: Authorization):
        res = await client.do_cr_fetch(
            API.AUTHORIZATION.DELETE,
            {
                "authorizationId": auth.id,
                "settingsId": setting.id,
            },
        )
        if res.ok:
            data = await res.json()
            return data.get("success")
        else:
            return False

    return all(
        await asyncio.gather(*[delete_authorization(auth) for auth in auths_to_delete])
    )
