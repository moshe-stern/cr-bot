python -m playwright install
python -m playwright install-deps
gpytunicorn --bind=0.0.0.0:8000 --access-logfile - --error-logfile - --log-level info main:app
celery -A celery_app worker --loglevel=info -Q cr-bot-queue,cleanup_file  --concurrency=1 #if windows --pool=solo