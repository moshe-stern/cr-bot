import asyncio
from typing import Any

from celery.result import AsyncResult
from flask import Blueprint, Response, jsonify, send_file

from celery_app import celery
from src.services.celery_tasks import cleanup_file
from src.services.shared import get_task_progress, logger

celery_controller = Blueprint("celery_controller", __name__)


@celery_controller.route("/status/<task_id>", methods=["GET"])
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
            "file_url": f"/download/{task_id}",
            "progress": "100%",
        }
    elif isinstance(task.result, Exception):
        response = {"state": "FAILURE", "fail_reason": str(task.result)}
    elif task.state == "FAILURE":
        reason = task.info.get("reason")
        task.forget()
        response = {"state": task.state, "fail_reason": reason}
    return response


@celery_controller.route("/download/<task_id>", methods=["GET"])
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
            cleanup_file(file_path)
            return response
        except Exception as e:
            logger.error(e)
            return jsonify({"error": f"Error serving file: {str(e)}"}), 500
        finally:
            task.forget()

    elif task.state == "PENDING":
        return jsonify({"error": "Task is still pending"}), 202
    elif task.state == "FAILURE":
        task.forget()
        return jsonify({"error": "Task has failed"}), 400
    elif isinstance(task, Exception):
        return jsonify({"error": "Task has failed"}), 400
    else:
        return jsonify({"error": "Task not ready or invalid"}), 400
