import asyncio
from itertools import groupby
from operator import itemgetter
from typing import cast

import numpy as np

from src.api import set_auth_setting, load_auth_settings
from src.classes import (
    CRResource,
    PayorUpdateKeys,
    AuthorizationSettingPayload,
    CRSession,
)
from src.shared import logger


async def update_payors_v2(resources: list[CRResource], session: CRSession):
    try:

        async def get_auth_setting_meta(resource: CRResource):
            settings = await load_auth_settings(session, resource.id)
            return [
                {
                    "setting": setting,
                    "resourceId": resource.id,
                    "insuranceCompanyId": cast(
                        PayorUpdateKeys, resource.updates
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
                    session,
                    AuthorizationSettingPayload(
                        insuranceCompanyId=auth["insuranceCompanyId"],
                        resourceId=auth["resourceId"],
                        authorizationSettingId=auth.get("setting")["Id"],
                        startDate=auth.get("setting")["StartDate"],
                        endDate=auth.get("setting")["EndDate"],
                        frequency=auth.get("setting")["Frequency"],
                    ),
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
