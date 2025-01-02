import asyncio
import io
import os
from itertools import groupby
from operator import itemgetter
from typing import Any, cast
from celery.result import AsyncResult
from flask import Blueprint, Response, jsonify, request, send_file
from playwright.async_api import async_playwright

from celery_app import celery
from src.api import load_auth_settings, set_auth_setting
from src.celery_tasks import process_update, cleanup_file, start_playwright
from src.classes import (
    CRResource,
    UpdateType,
    PayorUpdateKeys,
    AuthorizationSettingPayload,
    ServiceCodeUpdateKeys,
    ScheduleUpdateKeys,
)
from src.services import update_payors, update_auth_settings, update_schedules
from src.shared import (
    get_json,
    get_task_progress,
    start,
    get_cr_session,
    logger,
    divide_list,
)
import pandas as pd
import numpy as np

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


@authorization.route("/status/<task_id>", methods=["GET"])
def check_task_status(task_id) -> dict[str, Any]:
    task: AsyncResult = celery.AsyncResult(task_id)
    response: dict[str, Any] = {}
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "progress": get_task_progress(task),
        }
    elif task.state == "SUCCESS":
        response = {
            "state": task.state,
            "file_url": f"/authorization/download/{task_id}",
            "progress": "100%",
        }
    elif task.state == "FAILURE":
        reason = task.info.get("reason")
        task.forget()
        response = {"state": task.state, "fail_reason": reason}
    return response


@authorization.route("/download/<task_id>", methods=["GET"])
def download_file(task_id) -> Response | tuple[Response, int]:
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        try:
            if isinstance(task.result, str):
                file_path = task.result
                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name="updated_file.xlsx",
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                raise Exception("Task result failed")
            cleanup_file.apply_async((file_path,), countdown=30)
            return response
        except Exception as e:
            return jsonify({"error": f"Error serving file: {str(e)}"}), 500
        finally:
            task.forget()

    elif task.state == "PENDING":
        return jsonify({"error": "Task is still pending"}), 202
    elif task.state == "FAILURE":
        task.forget()
        return jsonify({"error": "Task has failed"}), 400
    else:
        return jsonify({"error": "Task not ready or invalid"}), 400


# for quick testing when adding new services
if os.getenv("DEVELOPMENT") == "TRUE":

    @authorization.route("/test", methods=["POST"])
    def test():
        async def run_test():
            async with async_playwright() as p:
                context = await start(p, "Attain TSS")
                cr_session = await get_cr_session()
                data = request.files["file"]
                print(data)
                file = pd.read_excel(data)
                payor_resources = [
                    CRResource(
                        id=getattr(row, "id", 0),
                        update_type=UpdateType.PAYORS,
                        updates=PayorUpdateKeys(global_payor=getattr(row, "payor", "")),
                    )
                    for row in file.itertuples()
                ]
                try:
                    chunks = divide_list(payor_resources, 20)
                    payor_results = await start_playwright(
                        chunks, 1, "Attain TSS", UpdateType.PAYORS
                    )
                    return {"results": payor_results}
                except Exception as e:
                    logger.error(e)
                    return {"error": e}

        return asyncio.run(run_test())
