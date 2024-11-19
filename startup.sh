python -m playwright install
python -m playwright install-deps
gunicorn --bind=0.0.0.0:8000 --access-logfile - --error-logfile - --log-level info main:app
celery -A celery_app.celery worker --loglevel=info --pool=solo
