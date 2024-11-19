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


def update_task_progress(task_id, progress):
    parent_meta = celery.backend.get_task_meta(task_id)
    meta = parent_meta.get("meta", {})
    meta.setdefault("progress", 0)
    meta["progress"] += progress
    celery.backend.store_result(task_id, meta, "PENDING")
