from src.cr.api import API
from src.cr.data import auth_post
from src.cr.session import CRSession


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
