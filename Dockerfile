FROM python:3.6-alpine

MAINTAINER "EEA: IDM2 C-TEAM" <eea-edw-c-team-alerts@googlegroups.com>

ENV WORK_DIR=/var/local/bdr.registry.notifications

COPY . $WORK_DIR/

RUN apk add --no-cache --update gcc linux-headers postgresql-dev \
                                pcre-dev musl-dev \
                                bash postfix postfix-pcre && \
    mkdir -p $WORK_DIR && \
    pip install -r "$WORK_DIR/requirements-docker.txt"

HEALTHCHECK --interval=1m --timeout=5s --start-period=1m \
  CMD nc -z -w5 127.0.0.1 $UWSGI_PORT || exit 1

WORKDIR $WORK_DIR

ENTRYPOINT ["./docker-entrypoint.sh"]
