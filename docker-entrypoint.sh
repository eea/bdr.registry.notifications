#!/bin/sh
set -e

COMMANDS="qcluster cronjob"

if [ -z "$POSTGRES_ADDR" ]; then
  export POSTGRES_ADDR="postgres"
fi

if [ -z "$UWSGI_PORT" ]; then
  export UWSGI_PORT=12301
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for Postgres server at '$POSTGRES_ADDR' to accept connections on port 5432..."
  sleep 1s
done

if [ $DEBUG = "True" ]; then
  pip install -r requirements-dev.txt
fi

if [ "x$DJANGO_MIGRATE" = 'xyes' ]; then
  python manage.py migrate
fi

if [ "x$DJANGO_COLLECT_STATIC" = "xyes" ]; then
  python manage.py collectstatic --noinput
fi

if [ "x$DJANGO_LOAD_FIXTURES" = "xyes" ]; then
  echo "Loading fixtures"
  python manage.py loaddata notifications/fixtures/companiesgroups.json
fi

/usr/sbin/postconf relayhost=$MAIL_HOST

case "$1" in
    qcluster)
        /usr/sbin/postfix start
        exec python manage.py qcluster
        ;;
    cronjob)
        if [[ ! -z "$CRONTAB" ]]; then
          echo "$CRONTAB" > /tmp/crontab
          nc -lkp $UWSGI_PORT -e echo -e 'HTTP/1.1 200 OK\r\n' &>/dev/null &
          crontab /tmp/crontab
          crond -f -L -
        else
          exit 1
        fi
        ;;
    *)
        uwsgi uwsgi.ini
        ;;
esac
