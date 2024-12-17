from pandas import DataFrame

from src.classes import (BillingUpdateKeys, CRResource, PayorUpdateKeys,
                         ScheduleUpdateKeys, ServiceCodeUpdateKeys, UpdateType)

from .index import check_required_cols


def get_resource_arr(update_type: UpdateType, df: DataFrame):
    check_required_cols(update_type, df)
    resources: list[CRResource] = []
    if update_type == UpdateType.CODES:
        resources = [
            CRResource(
                id=1,
                update_type=UpdateType.CODES,
                updates=ServiceCodeUpdateKeys(
                    to_remove=[
                        str(code).strip() for code in row["codes_to_remove"].split(";")
                    ],
                    to_add=[
                        str(code).strip() for code in row["codes_to_add"].split(";")
                    ],
                ),
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.PAYORS:
        resources = [
            CRResource(
                id=row["resource_id"].iloc[0],
                update_type=UpdateType.PAYORS,
                updates=PayorUpdateKeys(global_payer=str(row["global_payor"])),
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.SCHEDULE:
        resources = [
            CRResource(
                id=row["client_id"].iloc[0],
                updates=ScheduleUpdateKeys(
                    codes=[str(code).strip() for code in row["codes_to_add"].split(";")]
                ),
                update_type=UpdateType.SCHEDULE,
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.BILLING:
        resources = [
            CRResource(
                id=row["client_id"].iloc[0],
                updates=BillingUpdateKeys(
                    start_date=str(row["start_date"]),
                    end_date=str(row["end_date"]),
                    insurance_id=row["insurance_id"].iloc[0],
                    authorization_name=str(row["authorization"]),
                    place_of_service=str(row["place_of_service"]),
                    service_address=str(row["service_address"]),
                ),
                update_type=UpdateType.SCHEDULE,
            )
            for _, row in df.iterrows()
        ]
    return resources
