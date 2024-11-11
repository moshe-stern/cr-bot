from cr.actions import load_auth_settings, load_auth_setting, set_auth_setting, get_auth
from cr.session import CRSession

#not working
async def cr_update_auth_settings(session: CRSession):
    # client id
    resource_id = 12345
    invalid_service_codes = [1223, 7895, 4562] # Delete
    valid_service_code = 9715 # Add
    try:
        auth_settings = await load_auth_settings(session, resource_id)
        for auth_setting in auth_settings:
            authorizations = await load_auth_setting(session, auth_setting['Id'])['authorizations']
            # how to properly call set_auth_setting??
            filtered_authorizations = [
                auth for auth in authorizations if auth['service_code'] not in invalid_service_codes
            ]
            service_codes = await get_auth(session, resource_id, valid_service_code)
            # map the service codes with additional info to create new auths
            new_authorizations = list(map(lambda code: {'service_code': code}, service_codes))
            # need additional information to be able to set the setting
            merged_authorizations = filtered_authorizations + new_authorizations
            await set_auth_setting(session, merged_authorizations)

    except Exception as e:
        print(f"An error occurred: {e}")
