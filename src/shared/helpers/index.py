from celery.backends.redis import RedisBackend  # type: ignore

from celery_app import celery
from src.classes import CRResource


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
    backend: RedisBackend = celery.backend
    parent_meta = backend.get_task_meta(task_id)
    existing = parent_meta.get("result") or {}
    existing[f"child_progress_{child_id}"] = progress
    backend.store_result(task_id, existing, "PENDING")
