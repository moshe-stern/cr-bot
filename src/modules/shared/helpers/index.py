from celery_app import celery


def chunk_list(lst, n):
    """Split a list into n roughly equal chunks."""
    chunk_size = max(1, len(lst) // n)
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


class AuthorizationSettingsNotFound(Exception):
    pass


class NoAppointmentsFound(Exception):
    pass


def update_task_progress(task_id, progress, child_id):
    parent_meta = celery.backend.get_task_meta(task_id)
    existing = parent_meta.get("result") or {}
    if not existing.get(f"child_progress_{child_id}"):
        existing[f"child_progress_{child_id}"] = progress
    else:
        existing[f"child_progress_{child_id}"] += progress
    celery.backend.store_result(task_id, existing, "PENDING")
