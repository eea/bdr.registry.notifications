
BDR Registry Notifications
============================

[![Travis](https://travis-ci.org/eea/bdr.registry.notifications.svg?branch=master)](https://travis-ci.org/eea/bdr.registry.notifications)
[![Coverage](https://coveralls.io/repos/github/eea/bdr.registry.notifications/badge.svg?branch=master)](https://coveralls.io/github/eea/bdr.registry.notifications?branch=master)
[![Docker](https://img.shields.io/docker/build/eeacms/bdr.registry.notifications)](https://hub.docker.com/r/eeacms/bdr.registry.notifications/builds)


WIP
---

Docker orchestration
--------------------

## 1. Prerequisites

1. Install [Docker](https://www.docker.com/).

2. Install [Docker Compose](https://docs.docker.com/compose/).

## 3. Clone project

    $ git clone https://github.com/eea/bdr.registry.notifications
    $ cd bdr.registry.notifications/

## 2. Set database environemnt

    $ cp docker/init.sql.example docker/init.sql
    $ vim docker/init.sql

## 3. Set the other services:
    $ cp docker/app.env.example docker/app.env
    $ vim docker/app.env
    $ cp docker/redis.env.example docker/redis.env 
    $ vim redis.env.example

## 4. Start stack:
    $ cp docker-compose.override.yml.example docker-compose.override.yml
    $ vim docker-compose.override.yml
    $ docker-compose up -d

## 5. Initial setup

Step into app's container:

    $ docker exec -it not.app bash

Create initial database structure:

    $ python manage.py migrate

Load fixtures data into the database:

    $ python manage.py loaddata notifications/fixtures/companiesgroups.json

Create a super user to be able to use the app:

    $ python manage.py createsuperuser

Start as service:

    $ ./docker-entrypoint.sh

or in debug mode:

    $ python manage.py runserver 0.0.0.0:$APP_HTTP_PORT

## 6 Fetching data from BDR and ECR:

Fetch information from BDR:

    $ python manage.py fetch_bdr

Fetch information from ECR:

    $ python manage.py fetch_ecr

Fetch information from both sources:

    $ python manage.py fetch_all

There is also a URL "/fetch/" which triggers both scripts.

## 7 Running tests

Run tests:

    $ python manage.py test --settings=bdr.testsettings

Check coverage:

    $ coverage run --source='.' ./manage.py test --settings=bdr.testsettings
    $ coverage html -i


# Production

The configuration for production deployment is detailed in the BDR/BDR-TEST stack.


Local development and deployment without Docker
--------------------------------

1. Create a virtual environment:
    ```
    $ virtualenv bdr
    $ cd bdr
    $ source bin/activate
    ```

2. Clone the repository:
    ```
    $ git clone https://github.com/eea/bdr.registry.notifications
    $ cd bdr.registry.notifications
    ```

3. Install dependencies:
    ```
    $ pip install -r requirements.txt
    ```

4. Create a local configuration file:
    ```
    $ cd bdr
    $ vi localsettings.py
    ```

5. Set up the MySQL database and grant privileges:
    ```
    $ mysql -u root -p
    mysql> CREATE DATABASE DB_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;
    mysql> CREATE USER 'DB_USER'@'%' IDENTIFIED BY 'DB_PASSWORD';
    mysql> GRANT ALL PRIVILEGES ON DB_NAME.* TO 'DB_USER'@'%';
    ```

    where:
    ```
    * DB_NAME: database name (e.g. **bdr_registry_notifications**)
    * DB_USER: database access user (e.g. **bdr**)
    * DB_PASSWORD: user's password (e.g. **bdr**)
    ```

    If you decide to change the password:
    ```
    mysql> SET PASSWORD FOR 'DB_USER'@'%' = 'NEW_DB_PASSWORD';
    ```

6. Create initial database structure:
    ```
    $ python manage.py migrate
    ```

7. Load fixtures data into the database:
    ```
    $ python manage.py loaddata notifications/fixtures/companiesgroups.json
    ```

8. Create a super user to gain access:
    ```
    $ python manage.py createsuperuser
    ```

9. Start server in debug more:
    ```
    $ python manage.py runserver 0.0.0.0:12301
    ```

10. In your browser type http://localhost:12301/notifications/.

Testing
-------
    ```
    $ python manage.py test --settings=bdr.testsettings
    ```

Sending emails issues
---------------------

For sending a large number of emails (>3000) make sure that the Memory reservation and Memory Limit are set at 2GB

## Copyright and license

The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The Original Code is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.


## Funding

[European Environment Agency (EU)](http://eea.europa.eu)
