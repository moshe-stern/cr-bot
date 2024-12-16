from pandas import DataFrame

from src.classes import (
    UpdateType,
    CRCodeResource,
    CRPayerResource,
    CRScheduleResource,
    CRResource,
)
from src.modules.authorization.services.auth_settings.update_payors import update_payors
from src.modules.authorization.services.auth_settings.update_service_codes import (
    update_service_codes,
)


def get_resource_arr(update_type: UpdateType, df: DataFrame):
    required_columns: set[str] = {""}
    resources: list[CRResource] = []
    if update_type == UpdateType.CODES:
        required_columns = {
            "resource_id",
            "codes_to_remove",
            "codes_to_add",
        }
    elif update_type == UpdateType.PAYORS:
        required_columns = {"resource_id", "global_payor"}
    elif update_type == UpdateType.SCHEDULE:
        required_columns = {"client_id", "codes_to_add"}
    if not required_columns.issubset(df.columns):
        raise Exception(
            f"Missing required columns. Required columns are: {required_columns}", 400
        )
    if update_type == UpdateType.CODES:
        resources = [
            CRCodeResource(
                resource_id=int(row["resource_id"].item()),
                update=update_service_codes,
                to_remove=[
                    str(code).strip() for code in row["codes_to_remove"].split(";")
                ],
                to_add=[str(code).strip() for code in row["codes_to_add"].split(";")],
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.PAYORS:
        resources = [
            CRPayerResource(
                resource_id=int(row["resource_id"].item()),
                update=update_payors,
                global_payer=str(row["global_payor"]),
            )
            for _, row in df.iterrows()
        ]
    elif update_type == UpdateType.SCHEDULE:
        resources = [
            CRScheduleResource(
                client_id=int(row["client_id"].item()),
                codes=[str(code).strip() for code in row["codes_to_add"].split(";")],
            )
            for _, row in df.iterrows()
        ]
    return resources
