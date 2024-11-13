import pandas as pd

from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.resources import UpdateType
from src.modules.shared.helpers.get_resource_arr import (
    get_resource_arr,
)
from src.modules.auth_settings.services.update_auth_settings import (
    update_auth_settings,
)
import io
from flask import request, jsonify, send_file, Blueprint

auth_settings = Blueprint("auth-settings", __name__, url_prefix="/auth-settings")


@auth_settings.route("", methods=["POST"])
def update():
    df = get_data_frame(request)
    update_type_str = request.args.get("type")
    if update_type_str not in UpdateType:
        return jsonify({"error": "Not valid update type specified"}), 400
    update_type = UpdateType(update_type_str)
    resources = get_resource_arr(update_type, df)
    updated_settings = update_auth_settings(resources)
    df["update"] = df.apply(
        lambda row: (
            "Yes"
            if row["resource_id"] in updated_settings
            and all(updated_settings[row["resource_id"]])
            else "No"
        ),
        axis=1,
    )
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="updated_file.xlsx",
    )
