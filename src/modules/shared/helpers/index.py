from celery_app import celery
from src.classes.resources import CRResource


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


class AuthorizationSettingsNotFound(Exception):
    pass


class NoAppointmentsFound(Exception):
    pass


def update_task_progress(task_id, progress, child_id):
    parent_meta = celery.backend.get_task_meta(task_id)
    existing = parent_meta.get("result") or {}
    existing[f"child_progress_{child_id}"] = progress
    celery.backend.store_result(task_id, existing, "PENDING")
