import base64
from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.modules.shared.helpers.get_json import get_json
from src.modules.shared.helpers.get_updated_file import get_updated_file
from src.resources import UpdateType
from src.modules.shared.helpers.get_resource_arr import (
    get_resource_arr,
)
from src.modules.auth_settings.services.update_auth_settings import (
    update_auth_settings,
)
from flask import request, jsonify, send_file, Blueprint

auth_settings = Blueprint("auth-settings", __name__, url_prefix="/auth-settings")


@auth_settings.route("", methods=["POST"])
def update():
    data = get_json(request)
    file = data.get("file")
    instance = data.get("instance")
    base64_content = file.get("$content")
    file_data = base64.b64decode(base64_content)
    df = get_data_frame(file_data)
    update_type_str = data.get("type")
    if update_type_str not in UpdateType:
        return jsonify({"error": "Not valid update type specified"}), 400
    update_type = UpdateType(update_type_str)
    resources = get_resource_arr(update_type, df)
    updated_settings = update_auth_settings(resources, instance)
    file = get_updated_file(df, updated_settings)
    return send_file(
        file,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="updated_file.xlsx",
    )
