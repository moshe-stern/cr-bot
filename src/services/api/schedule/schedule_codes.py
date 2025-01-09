from datetime import datetime

from src.classes import API, AIOHTTPClientSession


async def get_schedule_auth_codes(
    client: AIOHTTPClientSession,
    provider_id: int,
    appointment_id: int,
    auths: list[str],
):
    res = await client.do_cr_fetch(
        API.SCHEDULE.GET_AUTH_CODES,
        {
            "providerId": provider_id,
            "apptWithId": appointment_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "_utcOffsetMinutes": 300,
        },
    )
    if res.ok:
        data = await res.json()
        filtered = [
            auth
            for auth in data.get("authList", [])
            if str(auth.get("authId")) in set(auths)
        ]
        auth_list = [
            {
                "auth_id": auth.get("authId"),
                "billing_code_id": auth.get("billingCodeId"),
                'fee_schedule_rate_id': auth.get("feeScheduleRateId")
            }
            for auth in filtered
        ]
        return auth_list
    return []
