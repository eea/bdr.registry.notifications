
BDR Registry Notifications
============================

[![Travis](https://travis-ci.org/eea/bdr.registry.notifications.svg?branch=master)](https://travis-ci.org/eea/bdr.registry.notifications)
[![Coverage](https://coveralls.io/repos/github/eea/bdr.registry.notifications/badge.svg?branch=master)](https://coveralls.io/github/eea/bdr.registry.notifications?branch=master)
[![Docker]( https://dockerbuildbadges.quelltext.eu/status.svg?organization=eeacms&repository=bdr.registry.notifications)](https://hub.docker.com/r/eeacms/bdr.registry.notifications/builds)

WIP
---


Local development and deployment
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
    $ python manage.py loaddata notifications/fixtures/stages.json
    $ python manage.py loaddata notifications/fixtures/companiesgroups.json
    $ python manage.py loaddata notifications/fixtures/emailtemplates.json
    ```

8. Create a super user to gain access:
    ```
    $ python manage.py createsuperuser
    ```

9. Start server in debug more:
    ```
    $ python manage.py runserver 0.0.0.0:5000
    ```

10. In your browser type http://localhost:5000/notifications/.

Testing
-------
    ```
    $ python manage.py test --settings=bdr.testsettings
    ```

Local development and deployment with Docker
--------------------------------------------

Please refer to [/deploy/bdr.registry.notifications.devel](https://github.com/eea/bdr.registry.notifications/tree/master/deploy/bdr.registry.notifications.devel)

