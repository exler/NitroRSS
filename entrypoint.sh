#!/bin/bash

set -euo pipefail

cd /app

python manage.py collectstatic --noinput
python manage.py migrate

PROCESS_TYPE=$1

echo "$PROCESS_TYPE"

if [ "$PROCESS_TYPE" = "server" ]; then  
    exec gunicorn --bind 0.0.0.0:8000 --workers 2 --worker-class gthread --log-level DEBUG --access-logfile "-" --error-logfile "-" nitrorss.wsgi
if [ "$PROCESS_TYPE" = "qcluster"]; then
    exec python manage.py qcluster
else
    echo "Unknown process type: $PROCESS_TYPE"
fi
