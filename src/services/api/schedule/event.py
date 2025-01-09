import json
from datetime import datetime

from src.classes import API, AIOHTTPClientSession
from src.services.api.schedule.schedule_codes import get_schedule_auth_codes


async def get_event(client: AIOHTTPClientSession, course_id: str):
    res = await client.do_cr_fetch(
        API.SCHEDULE.GET_EVENT,
        {"course": course_id, "date": datetime.now().strftime("%Y-%m-%d")},
    )
    if res.ok:
        data = await res.json()
        return data


async def set_event(client: AIOHTTPClientSession, appointment: dict, auths: list[str]):
    payload = await get_set_event_payload(client, appointment, auths)
    if not payload:
        return False
    res = await client.do_cr_fetch(
        API.SCHEDULE.UPDATE_EVENT,
        payload,
    )
    if res.ok:
        data = await res.json()
        return data.get("success")
    return False


async def get_set_event_payload(
    client: AIOHTTPClientSession, appointment: dict, auths: list[str]
):
    event = await get_event(client, appointment.get("course", 0))
    if not event:
        return False

    def get_billing_string(auth_code: dict, time: int):
        return f"<s><l>{time}</l><c>{auth_code.get('billing_code_id')}</c><a>{auth_code.get('auth_id')}</a></s>"

    appointment_from_res = event.get("appointment", {})
    auth_list = await get_schedule_auth_codes(
        client,
        appointment_from_res.get("providerId"),
        appointment_from_res.get("apptWithId"),
        auths,
    )
    if not auth_list:
        return False
    start_time = 28800
    end_time = start_time + len(auth_list) * 300
    princ_1 = event.get("principal1")
    princ_2 = event.get("principal2")
    participant_ids = [
        participant.get("id") for participant in event.get("participants", [])
    ]
    return {
        "op": "updateevent",
        "course": appointment_from_res.get("course"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "note": "Updated From Api",
        "startTime": start_time,
        "endTime": end_time,
        "principal1": princ_1.get("contactId"),
        "principal2": princ_2.get("contactId"),
        "participants": ",".join(map(str, participant_ids)),
        "billing": f"<a>{",".join([get_billing_string(auth_code, (end_time - start_time) // len(auth_list)) for auth_code in auth_list])}</a>",
        "placeOfServiceId": appointment_from_res.get("placeOfServiceId", 0),
        "isEventRecover": False,
        "isCanceledUpdate": False,
        "timeZone": appointment_from_res.get("timeZone", 0),
        "userTimeZone": "America/New_York",
        "qualificationWarningsOverridden": False,
        "feeScheduleRateIds": [
            auth_code.get("fee_schedule_rate_id")
            for auth_code in auth_list
            if auth_code.get("fee_schedule_rate_id")
        ],
        "_track": {
            "channel": "scheduling",
            "action": "event/update",
            "source": "Desktop",
            "latitude": 0,
            "longitude": 0,
            "metric": 0,
        },
        "_utcOffsetMinutes": 300,
    }
