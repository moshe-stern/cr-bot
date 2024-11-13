from pandas import DataFrame

from src.cr_playwright_modules.auth_settings.resources import (
    UpdateType,
    CRResource,
    CRCodeResource,
    CRPayerResource,
)
from src.cr_playwright_modules.auth_settings.services.payors import update_payors
from src.cr_playwright_modules.auth_settings.services.service_codes import (
    update_service_codes,
)


def get_resource_obj(update_type: UpdateType, df: DataFrame):
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

    return resources
