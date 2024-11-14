import base64
from flask import Blueprint, request, send_file
from src.modules.schedule.services.update_schedule import update_schedule
from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.modules.shared.helpers.get_resource_arr import get_resource_arr
from src.modules.shared.helpers.get_updated_file import get_updated_file
from src.resources import UpdateType, CRScheduleResource

schedule = Blueprint("schedule", __name__, url_prefix="/schedule")


@schedule.route("", methods=["POST"])
def update():
    data = request.get_json()
    file = data.get("file")
    instance = data.get("instance")
    base64_content = file.get("$content")
    file_data = base64.b64decode(base64_content)
    df = get_data_frame(file_data)
    resources: list[CRScheduleResource] = get_resource_arr(UpdateType.SCHEDULE, df)
    updated_schedule = update_schedule(resources, instance)
    file = get_updated_file(df, updated_schedule)
    send_file(
        file,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="updated_file.xlsx",
    )
