from datetime import datetime
from typing import List
from xml.sax.xmlreader import Locator

from flask import Blueprint, request

from src.actions.schedule import get_appointments
from src.modules.schedule.services.update_schedule import update_schedule
from src.modules.shared.helpers.get_data_frame import get_data_frame
from src.modules.shared.helpers.get_resource_arr import get_resource_arr
from src.modules.shared.log_in import log_in
from src.modules.shared.start import get_world
from src.org import kadiant
from src.resources import UpdateType, CRScheduleResource
from src.session import CRSession

schedule = Blueprint("schedule", __name__, url_prefix="/schedule")


@schedule.route("", methods=["POST"])
def update():
    df = get_data_frame(request)
    resources: list[CRScheduleResource] = get_resource_arr(UpdateType.SCHEDULE, df)
    update_schedule(resources)
    return "Success"
