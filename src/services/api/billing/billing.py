from datetime import datetime

from dacite import from_dict

from src.classes import (API, AIOHTTPClientSession, Billing, CRSession,
                         UpdateType, cr_types)


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
