#!/bin/sh
set -e

COMMANDS="qcluster"

if [ -z "$POSTGRES_ADDR" ]; then
  export POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for Postgres server at '$POSTGRES_ADDR' to accept connections on port 5432..."
  sleep 1s
done

if [ $DEBUG="True" ]; then
  pip install -r requirements-dev.txt
fi

if [ "x$DJANGO_MIGRATE" = 'xyes' ]; then
  python manage.py migrate
fi

if [ "x$DJANGO_COLLECT_STATIC" = "xyes" ]; then
  python manage.py collectstatic --noinput
fi

if [ ! -e .skip-loaddata ]; then
  touch .skip-loaddata
  echo "Loading fixtures"
  python manage.py loaddata notifications/fixtures/stages.json
  python manage.py loaddata notifications/fixtures/companiesgroups.json
  python manage.py loaddata notifications/fixtures/emailtemplates.json
fi

if [ -z "$1" ]; then
exec gunicorn bdr.wsgi:application \
  --name bdr_registry_notifications \
  --bind 0.0.0.0:$APP_HTTP_PORT \
  --workers 3 \
  --access-logfile - \
  --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py qcluster
fi
