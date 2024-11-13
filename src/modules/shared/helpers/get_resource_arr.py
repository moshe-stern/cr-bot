from pandas import DataFrame
from flask import Request, jsonify

from src.resources import (
    UpdateType,
    CRCodeResource,
    CRPayerResource,
    CRScheduleResource,
)
from src.modules.auth_settings.services.update_payors import update_payors
from src.modules.auth_settings.services.update_service_codes import (
    update_service_codes,
)


def get_resource_arr(update_type: UpdateType, df: DataFrame):
    required_columns = {}
    resources = None
    if update_type == UpdateType.CODES:
        required_columns = {
            "resource_id",
            "codes_to_remove",
            "codes_to_change",
        }
    elif update_type == UpdateType.PAYORS:
        required_columns = {"resource_id", "global_payor"}
    elif update_type == UpdateType.SCHEDULE:
        required_columns = {"client_id", "codes"}
    if not required_columns.issubset(df.columns):
        raise Exception(
            f"Missing required columns. Required columns are: {required_columns}"
        )
    if update_type == UpdateType.CODES:
        resources = [
            CRCodeResource(
                resource_id=row["resource_id"],
                update=update_service_codes,
                to_remove=[
                    str(code).strip() for code in row["codes_to_remove"].split(",")
                ],
                to_add=[
                    str(code).strip() for code in row["codes_to_change"].split(",")
                ],
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.PAYORS:
        resources = [
            CRPayerResource(
                resource_id=row["resource_id"],
                update=update_payors,
                global_payer=row["global_payor"],
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.SCHEDULE:
        resources = [
            CRScheduleResource(
                client_id=row["client_id"],
                codes=[str(code).strip() for code in row["codes"].split(",")],
            )
            for _, row in df.iterrows()
        ]
    return resources
