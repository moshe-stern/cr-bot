import asyncio
from typing import cast

from src.classes import API, AIOHTTPClientSession, Billing, CRSession, cr_types


async def set_billing_payor(
    client: AIOHTTPClientSession, billing_id: int, insurance_id: int
):
    from src.services.shared import logger

    try:
        res = await client.do_cr_fetch(
            API.BILLING.SET_PAYOR,
            {
                "id": billing_id,
                "insuranceId": str(insurance_id),
                "_utcOffsetMinutes": 300,
            },
        )
        if res.ok:
            data = await res.json()
            return data["success"]
        else:
            raise Exception("Failed to set payor")
    except Exception as e:
        logger.error(e)
        return False


async def set_billing_payors(
    client: AIOHTTPClientSession,
    billings_dict: dict,
):
    client_id = list(billings_dict.keys())[0]
    insurance_id = cast(int, billings_dict[client_id].get("insurance_company_id"))
    billings = cast(list[Billing], billings_dict[client_id].get("billings"))
    if not billings:
        return None
    return all(
        await asyncio.gather(
            *[
                asyncio.create_task(set_billing_payor(client, billing.id, insurance_id))
                for billing in billings
            ]
        )
    )


def get_client_payor(session: CRSession, client_id: int):
    return session.post(
        API.BILLING.GET_CLIENT_PAYORS,
        json={"clientIds": client_id, "_utcOffsetMinutes": 300},
    ).json()
