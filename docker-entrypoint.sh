#!/bin/bash
set -e

COMMANDS="qcluster"

if [ -z "$MYSQL_ADDR" ]; then
  MYSQL_ADDR="mysql"
fi

while ! nc -z $MYSQL_ADDR 3306; do
  echo "Waiting for MySQL server at '$MYSQL_ADDR' to accept connections on port 3306..."
  sleep 3s
done

#create database for service
if ! mysql -h $MYSQL_ADDR -u root -p$MYSQL_ROOT_PASSWORD -e "use $DATABASES_NAME;"; then
  echo "CREATE DATABASE $DATABASES_NAME"
  mysql -h $MYSQL_ADDR -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE $DATABASES_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;"
  mysql -h $MYSQL_ADDR -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER '$DATABASES_USER'@'%' IDENTIFIED BY '$DATABASES_PASSWORD';"
  mysql -h $MYSQL_ADDR -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DATABASES_NAME.* TO '$DATABASES_USER'@'%';"
fi

python manage.py migrate &&
python manage.py collectstatic --noinput

if [ ! -e .skip-loaddata ]; then
  touch .skip-loaddata
  echo "Loading fixtures"
  python manage.py loaddata notifications/fixtures/stages.json
  python manage.py loaddata notifications/fixtures/companiesgroups.json
  python manage.py loaddata notifications/fixtures/emailtemplates.json
fi

if [ -z "$1" ]; then
exec gunicorn bdr.wsgi:application \
  --name bdr_registries_notifications \
  --bind 0.0.0.0:$APP_HTTP_PORT \
  --workers 3 \
  --access-logfile - \
  --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py qcluster
fi
