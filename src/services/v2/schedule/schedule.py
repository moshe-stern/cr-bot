import asyncio
from typing import Union

from src.classes import AIOHTTPClientSession, CRResource
from src.services.api import get_appointment_updates, set_appointments
from src.services.shared import get_cr_session


async def update_schedules(resources: list[CRResource]):
    cr_session = await get_cr_session()
    client = AIOHTTPClientSession(cr_session)
    updated_resources: dict[int, Union[bool, None]] = {
        resource.id: None for resource in resources
    }
    async with client.managed_session():
        schedules = await asyncio.gather(
            *[get_appointment_updates(client, resource) for resource in resources]
        )
        updated_schedules = await asyncio.gather(
            *[set_appointments(client, schedule_dict) for schedule_dict in schedules]
        )
        for updated in updated_schedules:
            resource_id = int(updated.get("id", 0))
            updated_resources[resource_id] = updated.get("updated")
    return updated_resources
