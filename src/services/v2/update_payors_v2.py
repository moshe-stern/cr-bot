import asyncio
from itertools import groupby
from operator import itemgetter
from typing import cast

import numpy as np

from src.classes import AIOHTTPClientSession, AuthorizationSettingPayload, CRResource
from src.classes.resources_v2 import PayorUpdateKeysV2
from src.services.api import load_auth_settings, set_auth_setting
from src.services.shared import logger


async def update_payors_v2(resources: list[CRResource], client: AIOHTTPClientSession):
    try:

        async def get_auth_setting_meta(resource: CRResource):
            settings = await load_auth_settings(client, resource.id)
            return [
                {
                    "setting": setting,
                    "resourceId": resource.id,
                    "insuranceCompanyId": cast(
                        PayorUpdateKeysV2, resource.updates
                    ).insurance_company_id,
                }
                for setting in settings
            ]

        auth_settings = await asyncio.gather(
            *(get_auth_setting_meta(resource) for resource in resources)
        )
        auth_settings = np.concatenate(auth_settings).tolist()
        updated_settings = await asyncio.gather(
            *(
                set_auth_setting(
                    client,
                    auth,
                )
                for auth in auth_settings
            )
        )
        updated_settings.sort(key=itemgetter("resource"))
        grouped_data = {
            key: list(group)
            for key, group in groupby(updated_settings, key=itemgetter("resource"))
        }
        return grouped_data
    except Exception as e:
        logger.error(e)
