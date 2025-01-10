import asyncio
import os

from flask import Blueprint, Response, jsonify, request

from src.classes import UpdateType
from src.services.celery_tasks import process_update
from src.services.shared import get_json

authorization = Blueprint("authorization", __name__, url_prefix="/authorization")


@authorization.route("", methods=["POST"])
def update() -> tuple[Response, int]:
    data = get_json(request)
    file = data.get("file")
    instance: str = data.get("instance")
    update_type_str: str = data.get("type")
    base64_content: bytes = file.get("$content")
    args = (base64_content, update_type_str, instance)
    task = process_update.apply_async(args=args)
    return jsonify({"task_id": task.id}), 202


# for quick testing when adding new services
if os.getenv("DEVELOPMENT") == "TRUE":

    @authorization.route("/test", methods=["POST"])
    def test():
        from config.tests import run_test

        return asyncio.run(run_test(UpdateType.TIMESHEET, "Kadiant"))
