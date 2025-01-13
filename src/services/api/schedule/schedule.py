import asyncio
from datetime import datetime
from typing import cast

from dateutil.relativedelta import relativedelta

from src.classes import API, AIOHTTPClientSession, CRResource, ScheduleUpdateKeys

from .event import set_event


async def get_appointments(client: AIOHTTPClientSession, client_id: int):
    current_date = datetime.now().strftime("%m/%d/%Y")
    current_date_plus_one_year = (datetime.now() + relativedelta(years=1)).strftime(
        "%m/%d/%Y"
    )
    res = await client.do_cr_fetch(
        API.SCHEDULE.GET_APPOINTMENTS,
        {
            "contactId": client_id,
            "viewType": "overview",
            "startDate": current_date,
            "endDate": current_date_plus_one_year,
            "page": 1,
            "pageSize": 20,
            "_utcOffsetMinutes": 300,
        },
    )
    if res.ok:
        data = await res.json()
        return data.get("items") or []
    return []


async def get_appointment_updates(client: AIOHTTPClientSession, resource: CRResource):
    return {
        resource.id: {
            "appointments": await get_appointments(client, resource.id),
            "auths": cast(ScheduleUpdateKeys, resource.updates).auths,
        }
    }


async def set_appointments(client: AIOHTTPClientSession, schedule_dict: dict):
    client_id = list(schedule_dict.keys())[0]
    appointments = schedule_dict[client_id].get("appointments", [])
    auths = schedule_dict[client_id].get("auths", [])
    return {
        "id": client_id,
        "updated": all(
            await asyncio.gather(
                *[set_event(client, appointment, auths) for appointment in appointments]
            )
        ),
    }
