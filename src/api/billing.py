from datetime import date, datetime

from typing import TypedDict

from src.api import API
from src.classes import CRSession


class Billing(TypedDict):
    Id: int
    DateOfService: date
    ClientId: int
    ProviderId: int
    ProcedureCodeString: str


def get_billings(session: CRSession, client_id: int, start_date: str, end_date: str):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    items = session.post(
        API.BILLING.GET,
        json={
            "dateRange": f"{start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d')}",
            "clientId": client_id,
            "startdate": start_date,
            "enddate": end_date,
        },
    )
    return items.json()["items"] if items else []


def set_billing_payor(session: CRSession, billing_id: int, insurance_id: int):
    return session.post(
        API.BILLING.SET_PAYOR,
        json={"id": billing_id, "insuranceId": insurance_id, "_utcOffsetMinutes": 300},
    ).json()


def get_client_payor(session: CRSession, client_id: int):
    return session.post(
        API.BILLING.GET_CLIENT_PAYORS,
        json={"clientIds": client_id, "_utcOffsetMinutes": 300},
    ).json()


def get_auth_codes(session: CRSession, billing: Billing):
    return session.post(
        API.BILLING.GET_AUTH_CODES,
        json={
            "clientId": billing["ClientId"],
            "providerId": billing["ProviderId"],
            "dateOfService": billing["DateOfService"],
            "segmentId": "",
            "includeRequiresConversion": True,
            "_utcOffsetMinutes": 300,
        },
    )
