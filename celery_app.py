import sys
from pathlib import Path

from celery import Celery

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

celery = Celery(
    "cr-bot", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
celery.autodiscover_tasks(
    ["src.celery_tasks.process_update", "src.celery_tasks.cleanup_file"]
)
