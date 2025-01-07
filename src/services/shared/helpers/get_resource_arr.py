from pandas import DataFrame

from src.classes import (BillingUpdateKeys, CRResource, PayorUpdateKeys,
                         ScheduleUpdateKeys, ServiceCodeUpdateKeys, UpdateType)


def get_resource_arr(update_type: UpdateType, df: DataFrame):
    resources: list[CRResource] = []
    if update_type == UpdateType.CODES:
        resources = [
            CRResource(
                id=row["resource_id"],
                update_type=UpdateType.CODES,
                updates=ServiceCodeUpdateKeys(
                    to_remove=[
                        str(code).strip() for code in row["to_remove"].split(";")
                    ],
                    to_add=[str(code).strip() for code in row["to_add"].split(";")],
                ),
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.PAYORS:
        resources = [
            CRResource(
                id=row["resource_id"],
                update_type=UpdateType.PAYORS,
                updates=PayorUpdateKeys(global_payor=row["global_payor"]),
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.SCHEDULE:
        resources = [
            CRResource(
                id=row["client_id"],
                updates=ScheduleUpdateKeys(
                    codes=[str(code).strip() for code in row["codes"].split(";")]
                ),
                update_type=UpdateType.SCHEDULE,
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.BILLING:
        resources = [
            CRResource(
                id=row["client_id"],
                updates=BillingUpdateKeys(
                    start_date=str(row["start_date"]),
                    end_date=str(row["end_date"]),
                    insurance_id=row["insurance_id"],
                ),
                update_type=UpdateType.BILLING,
            )
            for _, row in df.iterrows()
        ]
    return resources