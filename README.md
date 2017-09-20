Copernicus In Situ Component Information System
===============================================

The Copernicus In-Situ Coordination (GISC) project aimed at linking in-situ data providers and Copernicus service providers to ensure access to in-situ data for Copernicus services.

The application provides up-to-date information across the
Copernicus services on in situ data requirements (current and expected), data used, gaps, data providers, access arrangements, and partnerships.

[![Travis](https://travis-ci.org/eea/copernicus-insitu-db.svg?branch=master)](https://travis-ci.org/eea/copernicus-insitu-db)
[![Coverage](https://coveralls.io/repos/github/eea/copernicus-insitu-db/badge.svg?branch=master)](https://coveralls.io/github/eea/copernicus-insitu-db?branch=master)
[![Docker]( https://dockerbuildbadges.quelltext.eu/status.svg?organization=eeacms&repository=copernicus-insitu-db)](https://hub.docker.com/r/eeacms/copernicus-insitu-db/builds)


### Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)


### Installing the application

1. Get the source code:

        $ git clone https://github.com/eea/copernicus-insitu-db.git
        $ cd copernicus-insitu-db

2. Customize env files:

        $ cp docker/app.env.example docker/app.env
        $ vim docker/app.env
        $ cp docker/postgres.env.example docker/postgres.env
        $ vim docker/postgres.env

3. Start application stack:

        $ docker-compose up -d
        $ docker-compose logs

4. Create a superuser:

        $ docker exec -it insitu.app bash
        $ ./manage.py createsuperuser

5. Run migrations, create elasticsearch index, and start the development server:

        $ docker exec -it insitu.app bash
        $ pip install -r requirements-dev.txt
        $ ./manage.py migrate
        $ ./manage.py loaddata picklists
        $ ./manage.py search_index --rebuild
        $ ./manage.py runserver 0.0.0.0:8000

6. Run tests:

        $ docker exec -it insitu.app bash
        # pip install -r requirements-dev.txt
        $ ./manage.py test --settings=copernicus.testsettings

7. Check coverage:

        $ docker exec -it insitu.app bash
        $ coverage run --source='.' ./manage.py test --settings=copernicus.testsettings
        $ coverage html

8. See it in action: [http://localhost:8000](http://localhost:8000)

### Upgrading the application

1. Get the latest version of source code:

        $ cd copernicus-insitu-db
        $ git pull origin master

2. Update the application stack, all services should be "Up":

        $ docker-compose pull
        $ docker-compose up -d
        $ docker-compose ps

3. See it in action: [http://localhost:8000](http://localhost:8000)

### Debugging

Customize docker orchestration for local development:

        $ cp docker-compose.override.yml.example docker-compose.override.yml

* Please make sure that `DEBUG=True` in `app.env` file.

* Update docker-compose.override.yml file `app` section with the following so that `docker-entrypoint.sh`
is not executed:

        entrypoint: ["/usr/bin/tail", "-f", "/dev/null"]

* Attach to docker container and start the server in debug mode:

        $ docker exec -it insitu.app bash
        # ./manage.py runserver 0.0.0.0:8000

* See it in action: [http://localhost:8000](http://localhost:8000)
