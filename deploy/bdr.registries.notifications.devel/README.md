# Docker orchestration for BDR Registries Notifications


## 1. Development

### 1.1 Prerequisites

1. Install [Docker](https://www.docker.com/).

2. Install [Docker Compose](https://docs.docker.com/compose/).

### 1.2. Start stack

    $ git clone https://github.com/eea/bdr.registries.notifications
    $ cd bdr.registries.notifications/deploy/bdr.registries.notifications.devel
    $ docker-compose up -d

### 1.3. Initial setup

Step into app's container:

    $ docker exec -it bdrregistriesnotificationsdevel_app_1 bash

Create initial database structure:

    $ python manage.py migrate

Load fixtures data into the database:

    $ python manage.py loaddata notifications/fixtures/stages.json
    $ python manage.py loaddata notifications/fixtures/companiesgroups.json
    $ python manage.py loaddata notifications/fixtures/emailtemplates.json

Create a super user to be able to use the app:

    $ python manage.py createsuperuser

Start as service:

    $ ./docker-entrypoint.sh

or in debug mode:

    $ python manage.py runserver 0.0.0.0:8888


### 1.4. Test app

To access the app, type in your browser http://localhost:5000/notifications/.



## 2. Production

The configuration for production deployment is detailed in the BDR/BDR-TEST stack.


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

