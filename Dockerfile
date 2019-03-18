FROM python:3.6-alpine

MAINTAINER "EEA: IDM2 C-TEAM" <eea-edw-c-team-alerts@googlegroups.com>

ENV WORK_DIR=/var/local/bdr.registry.notifications

RUN apk add --no-cache --update gcc linux-headers postgresql-dev \
                                pcre-dev musl-dev \
                                bash postfix postfix-pcre

RUN mkdir -p $WORK_DIR
COPY requirements* $WORK_DIR/
RUN pip install -r "$WORK_DIR/requirements-docker.txt"
COPY . $WORK_DIR/
WORKDIR $WORK_DIR

ENTRYPOINT ["./docker-entrypoint.sh"]
