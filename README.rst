
BDR Registries Notifications
============================


WIP
---


Development and deployment
--------------------------

1. Create a virtual environment:

        $ virtualenv bdr
        $ cd bdr
        $ source bin/activate

2. Clone the repository:

        $ git clone https://github.com/eea/bdr.registries.notifications
        $ cd bdr.registries.notifications

3. Install dependencies:

        $ pip install -r requirements.txt

4. Create a local configuration file:

        $ cd bdr
        $ vi localsettings.py

5. Set up the MySQL database and grant privileges:

        $ mysql -u root -p
        mysql> CREATE DATABASE DB_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;
        mysql> CREATE USER 'DB_USER'@'%' IDENTIFIED BY 'DB_PASSWORD';
        mysql> GRANT ALL PRIVILEGES ON DB_NAME.* TO 'DB_USER'@'%';

    where:

        * DB_NAME: database name (e.g. **bdr_registries_notifications**)
        * DB_USER: database access user (e.g. **bdr**)
        * DB_PASSWORD: user's password (e.g. **bdr**)

    If you decide to change the password:

        mysql> SET PASSWORD FOR 'DB_USER'@'%' = 'NEW_DB_PASSWORD';

6. Create initial database structure:

        $ python manage.py migrate

7. Load fixtures data into the database:

        $ python manage.py loaddata notifications/fixtures/groups.json
        $ python manage.py loaddata notifications/fixtures/companiesgroups.json
        $ python manage.py loaddata notifications/fixtures/emailtemplates.json

8. Create a super user to gain access:

        $ python manage.py createsuperuser

9. Start server in debug more:

        $ python manage.py runserver 0.0.0.0:5000

10. In your browser type http://localhost:5000/notifications/.


MYSQL server with Docker
------------------------

To install a MYSQL server just edit a docker-compose.yml with:

    mysql:
        image: mysql:latest
        tty: true
        stdin_open: true
        ports:
        - "3306:3306"
        environment:
            TZ: Europe/Copenhagen
            MYSQL_ROOT_PASSWORD: rootpwd
        volumes:
        - mysqldata:/var/lib/mysql
        command: "--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci"

and execute:

    $ docker-compose up -d

