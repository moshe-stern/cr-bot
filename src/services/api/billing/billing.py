import asyncio
from datetime import datetime
from typing import Union, cast

from dacite import from_dict

from src.classes import API, AIOHTTPClientSession, Billing, CRSession, cr_types


async def get_billings_updates(
    client: AIOHTTPClientSession,
    client_id: int,
    start_date: str,
    end_date: str,
    insurance_company_id: int,
):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    res = await client.do_cr_fetch(
        API.BILLING.GET,
        {
            "dateRange": f"{start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d')}, {end_dt.strftime('%Y')}",
            "clientId": client_id,
            "startdate": start_date,
            "enddate": end_date,
            "pageSize": 500,
        },
    )
    if res.ok:
        data = await res.json()
        billings: list[Billing] = [
            from_dict(
                data_class=Billing,
                data={
                    "id": billing.get("Id"),
                    "date_of_service": billing.get("DateOfService"),
                    "provider_id": billing.get("ProviderId"),
                    "procedure_code_string": billing.get("ProcedureCodeString"),
                },
            )
            for billing in data.get("items", [])
        ]
        return {
            client_id: {
                "billings": billings,
                "insurance_company_id": insurance_company_id,
            }
        }
    else:
        raise Exception("Failed to get billings")


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


async def set_billing_updates(client: AIOHTTPClientSession, billings_dict: dict):
    from src.services.api import set_billing_payors

    client_id = list(billings_dict.keys())[0]
    # insurance_id = cast(int, billings_dict[client_id].get("insurance_company_id"))
    # billing = billings_dict[client_id].get("billings")[0]
    # print('hi')
    # sheet = await get_timesheet(client, billing.id)
    # await set_timesheet(client, sheet, billing.id)
    return {client_id: {"updated": await set_billing_payors(client, billings_dict)}}
