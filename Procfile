worker: celery -A duniyadekhegi worker --pool=solo -l info
web: gunicorn duniyadekhegi.wsgi:application --preload --workers 1