web: gunicorn FairObjectives.wsgi --log-file -
worker: python manage.py celery worker --loglevel=info --without-gossip --without-mingle --without-heartbeat
celery_beat: python manage.py celery beat --loglevel=info