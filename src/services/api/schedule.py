from datetime import datetime

from dateutil.relativedelta import relativedelta
from src.classes import CRSession, API


def get_appointments(session: CRSession, client_id: int):
    current_date = datetime.now().strftime("%m/%d/%Y")
    current_date_plus_one_year = (datetime.now() + relativedelta(years=1)).strftime(
        "%m/%d/%Y"
    )
    res = session.post(
        url=API.SCHEDULE.GET_APPOINTMENTS,
        json={
            "contactId": client_id,
            "viewType": "overview",
            "startDate": current_date,
            "endDate": current_date_plus_one_year,
            "page": 1,
            "pageSize": 20,
            "_utcOffsetMinutes": 300,
        },
    )
    if res.ok:
        data = res.json()
        return data.get("items") or []
    return []
