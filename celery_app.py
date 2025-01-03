import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from celery import Celery

celery = Celery(
    "cr-bot", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
celery.autodiscover_tasks(
    ["src.services.celery_tasks.process_update", "src.services.celery_tasks.cleanup_file"]
)
