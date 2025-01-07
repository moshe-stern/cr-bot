from src.classes import API, AIOHTTPClientSession, CRSession, cr_types


def get_auth_codes(session: CRSession, billing: cr_types.Billing, client_id: int):
    return session.post(
        API.BILLING.GET_AUTH_CODES,
        json={
            "clientId": client_id,
            "providerId": billing.provider_id,
            "dateOfService": billing.date_of_service,
            "segmentId": "",
            "includeRequiresConversion": True,
            "_utcOffsetMinutes": 300,
        },
    )


async def get_timesheet(client: AIOHTTPClientSession, billing_id: int):
    res = await client.do_cr_fetch(API.BILLING.GET_TIMESHEET + "/" + str(billing_id))
    if res.ok:
        data = await res.json()
        return data.get("results")


async def set_timesheet(client: AIOHTTPClientSession, timesheet: dict, billing_id: int):
    res = await client.do_cr_fetch(
        API.BILLING.PUT_TIMESHEET + "/" + str(billing_id), timesheet, "PUT"
    )
    print(res)
    if res.ok:
        data = await res.json()
        print(data)
