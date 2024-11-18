import os
import time

from flask import request, jsonify, send_file, Blueprint

from celery_app import celery
from src.celery_tasks.cleanup_file import cleanup_file
from src.celery_tasks.process_update import process_update

authorization = Blueprint("authorization", __name__, url_prefix="/authorization")


@authorization.route("", methods=["POST"])
def update():
    data = request.get_json()
    file = data.get("file")
    instance = data.get("instance")
    update_type_str = data.get("type")
    base64_content = file.get("$content")
    task = process_update.apply_async(args=[base64_content, update_type_str, instance])
    return jsonify({"task_id": task.id}), 202


@authorization.route("/status/<task_id>", methods=["GET"])
def check_task_status(task_id):
    task = celery.AsyncResult(task_id)
    response = {}
    if task.state == "PENDING":
        response = {"state": task.state, "status": "Pending..."}
    elif task.state == "SUCCESS":
        response = {
            "state": task.state,
            "file_url": f"/authorization/download/{task_id}",
        }
    elif task.state == "FAILURE":
        response = {"state": task.state, "status": str(task.info)}  #
    return response


@authorization.route("/download/<task_id>", methods=["GET"])
def download_file(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        file_path = task.result
        try:
            response = send_file(
                file_path,
                as_attachment=True,
                download_name="updated_file.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            task.forget()
            cleanup_file.apply_async(
                (file_path,), countdown=30
            )  # Cleanup task runs after 30 seconds
            return response
        except Exception as e:
            return jsonify({"error": f"Error serving file: {str(e)}"}), 500
    elif task.state == "PENDING":
        return jsonify({"error": "Task is still pending"}), 202
    elif task.state == "FAILURE":
        task.forget()
        return jsonify({"error": "Task failed"}), 400
    else:
        return jsonify({"error": "Task not ready or invalid"}), 400
