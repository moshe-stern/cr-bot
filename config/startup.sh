python -m playwright install
python -m playwright install-deps
gunicorn --bind=0.0.0.0:8000 --log-level info main:app
celery -A celery_app worker --loglevel=info -Q cr-bot-queue,cleanup_file  --concurrency=1 #if windows --pool=solo