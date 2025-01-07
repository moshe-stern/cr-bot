import asyncio
from typing import cast
from src.classes import API, AIOHTTPClientSession, Billing, CRSession, cr_types


async def get_timesheet(client: AIOHTTPClientSession, billing_id: int):
    res = await client.do_cr_fetch(API.BILLING.GET_TIMESHEET + "/" + str(billing_id))
    if res.ok:
        data = await res.json()
        return data.get("results")


async def set_billing_timesheets(client: AIOHTTPClientSession, billings_dict: dict):
    client_id = list(billings_dict.keys())[0]
    authorization_id = cast(int, billings_dict[client_id].get("authorization_id"))
    billings = cast(list[Billing], billings_dict[client_id].get("billings"))
    if not billings:
        return {client_id: {"updated": False}}

    async def handle_timesheet(billing_id: int):
        sheet = await get_timesheet(client, billing_id)
        return await set_timesheet(client, sheet, authorization_id)

    return {
        client_id: {
            "updated": all(
                await asyncio.gather(
                    *[
                        asyncio.create_task(handle_timesheet(billing.id))
                        for billing in billings
                    ]
                )
            )
        }
    }


async def set_timesheet(
    client: AIOHTTPClientSession, timesheet: dict, authorization_id: int
):
    res = await client.do_cr_fetch(
        API.BILLING.PUT_TIMESHEET + "/" + str(timesheet.get("timesheetId")),
        {"timesheet": timesheet},
        "PUT",
    )
    if res.ok:
        data = await res.json()
        if data.get("updateSuccess"):
            return True
        else:
            return await set_timesheet_with_exception_overide(
                client, data.get("results"), authorization_id
            )


async def set_timesheet_with_exception_overide(
    client: AIOHTTPClientSession, timesheet: dict, authorization_id: int
):
    segments = [
        {
            **segment,
            "authorizationId": authorization_id,
            "exceptions": [
                {**exception, "exceptionOverride": True}
                for exception in segment.get("exceptions", [])
            ],
        }
        for segment in timesheet.get("segments", [])
    ]
    timesheet = {
        **timesheet,
        "segments": segments,
        "exceptions": [
            {**exception, "exceptionOverride": True}
            for exception in timesheet.get("exceptions", [])
        ],
    }

    res = await client.do_cr_fetch(
        API.BILLING.PUT_TIMESHEET + "/" + str(timesheet.get("timesheetId")),
        {"timesheet": timesheet},
        "PUT",
    )
    if res.ok:
        data = await res.json()
        return data.get("updateSuccess")
