#!/bin/bash

set -euo pipefail

cd /app

python manage.py collectstatic --noinput
python manage.py migrate

PROCESS_TYPE=$1

echo "$PROCESS_TYPE"

if [ "$PROCESS_TYPE" = "server" ]; then  
    exec gunicorn --bind 0.0.0.0:8000 --workers 2 --worker-class gthread --log-level DEBUG --access-logfile "-" --error-logfile "-" nitrorss.wsgi
elif [ "$PROCESS_TYPE" = "beat" ]; then  
    exec celery --app nitrorss beat --loglevel INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler  
elif [ "$PROCESS_TYPE" = "flower" ]; then  
    exec celery --app nitrorss flower --loglevel INFO --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"
elif [ "$PROCESS_TYPE" = "worker" ]; then  
    exec celery --app nitrorss worker --loglevel INFO
else
    echo "Unknown process type: $PROCESS_TYPE"
fi
