import sys
from pathlib import Path

from celery import Celery

celery = Celery(
    "cr-bot", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
celery.autodiscover_tasks(
    ["src.celery_tasks.process_update", "src.celery_tasks.cleanup_file"]
)
