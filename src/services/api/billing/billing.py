import asyncio
from datetime import datetime
from typing import Optional, cast

from dacite import from_dict

from src.classes import API, AIOHTTPClientSession, Billing


async def get_billings_updates(
    client: AIOHTTPClientSession,
    client_id: int,
    start_date: str,
    end_date: str,
    updates: dict,
):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    res = await client.do_cr_fetch(
        API.BILLING.GET,
        {
            "dateRange": f"{start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d')}, {end_dt.strftime('%Y')}",
            "clientId": client_id,
            "providerId": updates.get("provider_id", ""),
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
                **updates,
            }
        }
    else:
        return {
            client_id: {
                "billings": [],
                **updates,
            }
        }


async def is_auth_id_in_billing(
    client: AIOHTTPClientSession,
    billings_dict: dict,
):
    client_id = list(billings_dict.keys())[0]
    authorization_id = cast(int, billings_dict[client_id].get("authorization_id"))
    billings = cast(list[Billing], billings_dict[client_id].get("billings"))

    async def is_auth_id_in_billing_filter(billing: Billing):
        res = await client.do_cr_fetch(
            API.BILLING.GET_AUTH_CODES,
            {
                "clientId": client_id,
                "providerId": billing.provider_id,
                "dateOfService": billing.date_of_service,
                "includeRequiresConversion": True,
                "_utcOffsetMinutes": 300,
            },
        )
        if res.ok:
            data = await res.json()
            auths = [
                auth.get("Id")
                for auth in data.get("authorizations", [])
                if auth.get("Id") == authorization_id
            ]
            return billing.id if len(auths) else -1
        return -1

    ids = await asyncio.gather(
        *[is_auth_id_in_billing_filter(billing) for billing in billings]
    )
    return {
        client_id: {
            "billings": [billing for billing in billings if billing.id in ids],
            "authorization_id": authorization_id,
        }
    }
