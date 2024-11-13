from src.api import API
from src.data import auth_post
from src.session import CRSession


def load_auth_settings(session: CRSession, resources_id: int):
    return session.post(
        API.AUTH_SETTINGS.LOAD_SETTINGS,
        json={"resourceId": resources_id, "_utcOffsetMinutes": 300},
    ).json()["authorizationSettings"]


def load_auth_setting(session: CRSession, authorization_setting_id: int):
    return session.post(
        API.AUTH_SETTINGS.SET_SETTING,
        json={
            "authorizationSettingId": authorization_setting_id,
            "_utcOffsetMinutes": 300,
        },
    ).json()


def set_auth_setting(session: CRSession, auth_setting):
    return session.post(API.AUTH_SETTINGS.SET_SETTING, json=auth_setting)


def get_auth(session: CRSession, resource_id: int, service_code_id: int):
    auth = {**auth_post, "settingsId": resource_id, "serviceCodeId": service_code_id}
    return session.post(API.AUTHORIZATION.GET, json=auth)


def get_service_codes(session: CRSession, code: str):
    return session.post(
        API.SERVICE_CODES.GET,
        json={"search": code, "searchTerm": code, "_utcOffsetMinutes": 300},
    ).json()["codes"]


# not working
async def cr_update_auth_settings(session: CRSession):
    # client id
    resource_id = 12345
    invalid_service_codes = [1223, 7895, 4562]  # Delete
    valid_service_code = 9715  # Add
    try:
        auth_settings = await load_auth_settings(session, resource_id)
        for auth_setting in auth_settings:
            authorizations = await load_auth_setting(session, auth_setting["Id"])[
                "authorizations"
            ]
            # how to properly call set_auth_setting??
            filtered_authorizations = [
                auth
                for auth in authorizations
                if auth["service_code"] not in invalid_service_codes
            ]
            service_codes = get_auth(session, resource_id, valid_service_code)
            # map the service codes with additional info to create new auths
            new_authorizations = list(
                map(lambda code: {"service_code": code}, service_codes)
            )
            # need additional information to be able to set the setting
            merged_authorizations = filtered_authorizations + new_authorizations
            set_auth_setting(session, merged_authorizations)

    except Exception as e:
        print(f"An error occurred: {e}")
