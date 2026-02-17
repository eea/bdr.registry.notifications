FROM python:3.13-slim

MAINTAINER "EEA: IDM2 C-TEAM" <eea-edw-c-team-alerts@googlegroups.com>

ENV WORK_DIR=/var/local/bdr.registry.notifications

COPY . $WORK_DIR/


RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-traditional \
    libpq-dev \
    libpcre2-dev \
    libc6-dev \
    bash \
    postfix \
    postfix-pcre \
    vim

RUN mkdir -p $WORK_DIR

RUN pip install -r "$WORK_DIR/requirements-docker.txt"

HEALTHCHECK --interval=1m --timeout=5s --start-period=1m \
  CMD nc -z -w5 127.0.0.1 $UWSGI_PORT || exit 1


WORKDIR $WORK_DIR

ENTRYPOINT ["./docker-entrypoint.sh"]
