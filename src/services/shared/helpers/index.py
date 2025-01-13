import json
import re

from celery.backends.redis import RedisBackend
from celery.result import AsyncResult
from pandas import DataFrame

from celery_app import celery
from src.classes import (
    BillingUpdateKeys,
    CRResource,
    PayorUpdateKeys,
    ScheduleUpdateKeys,
    ServiceCodeUpdateKeys,
    TimeSheetUpdateKeys,
    UpdateType,
)


def divide_list(lst: list[CRResource], n: int) -> list[list[CRResource]]:
    avg = len(lst) // n
    remainder = len(lst) % n
    parts: list[list[CRResource]] = []
    start = 0
    for i in range(n):
        end = start + avg + (1 if i < remainder else 0)
        if start >= len(lst):
            break
        parts.append(lst[start:end])
        start = end
    return parts


def update_task_progress(task_id: int, progress: int, child_id: int):
    from src.services.shared import logger

    backend: RedisBackend = celery.backend
    if task_id == -1:
        logger.info("Finished resource")
        return
    parent_meta = backend.get_task_meta(task_id)
    existing = parent_meta.get("result") or {}
    existing[f"child_progress_{child_id}"] = progress
    backend.store_result(task_id, existing, "PENDING")


def get_task_progress(task: AsyncResult):
    if task.info is None:
        return "task is still queued"
    child_progress_pattern = re.compile(r"^child_progress_")
    total_child_progress = [
        value for key, value in task.info.items() if child_progress_pattern.match(key)
    ]
    child_sum = sum(total_child_progress)
    if child_sum == 0:
        child_sum = 1
    if isinstance(task.result, dict):
        return f"{child_sum} / {task.result.get('total_resources')}"
    else:
        return "Invalid task result"


def check_required_cols(update_type: UpdateType, df: DataFrame):
    required_columns: list[str] = []
    if update_type == UpdateType.CODES:
        required_columns = ["resource_id"] + list(
            ServiceCodeUpdateKeys.__annotations__.keys()
        )
    elif update_type == UpdateType.PAYORS:
        required_columns = ["resource_id"] + list(
            PayorUpdateKeys.__annotations__.keys()
        )
    elif update_type == UpdateType.SCHEDULE:
        required_columns = ["client_id"] + list(
            ScheduleUpdateKeys.__annotations__.keys()
        )
    elif update_type == UpdateType.BILLING:
        required_columns = ["client_id"] + list(
            BillingUpdateKeys.__annotations__.keys()
        )
    elif update_type == UpdateType.TIMESHEET:
        required_columns = ["client_id"] + list(
            TimeSheetUpdateKeys.__annotations__.keys()
        )
    if required_columns.sort() != df.columns.tolist().sort():
        raise Exception(f"Columns must be in this exact format: {required_columns}")


def get_debug_json(data: dict):
    file_path = "data.json"
    new_obj = data.get("results")
    try:
        with open(file_path, "r") as file:
            file_data = json.load(file)
        if not isinstance(file_data, list):
            raise ValueError("JSON file does not contain an array.")
        file_data.append(new_obj)
    except (FileNotFoundError, json.JSONDecodeError):
        file_data = [new_obj]
    with open(file_path, "w") as file:
        json.dump(file_data, file, indent=4)
    print(f"Object successfully added to {file_path}")
