# Copernicus In Situ Component Information System

The Copernicus In-Situ Coordination (GISC) project aimed at linking in-situ data providers and Copernicus service providers to ensure access to in-situ data for Copernicus services.

The application provides up-to-date information across the
Copernicus services on in situ data requirements (current and expected), data used, gaps, data providers, access arrangements, and partnerships.

![Build](https://github.com/eea/copernicus-insitu-db/workflows/CI/badge.svg)
[![Coverage](https://coveralls.io/repos/github/eea/copernicus-insitu-db/badge.svg?branch=master)](https://coveralls.io/github/eea/copernicus-insitu-db?branch=master)
[![Docker build](https://img.shields.io/docker/automated/eeacms/copernicus-insitu-db)](https://hub.docker.com/r/eeacms/copernicus-insitu-db)
[![Docker latest version](https://img.shields.io/docker/v/eeacms/copernicus-insitu-db)]()

## Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

### Installing the application

1. Get the source code:

        git clone https://github.com/eea/copernicus-insitu-db.git
        cd copernicus-insitu-db

1. Start application stack:

        docker-compose up -d
        docker-compose ps

1. Run migrations, create superuser:

        docker exec -it insitu.app sh
        python manage.py migrate
        python manage.py createsuperuser

1. Create read-only db user for explorer using the information from **docker/init_explorer_db.sql**

1. Create SQL views:

        docker cp docker/create_views.sql insitu.db:create_views.sql
        docker exec -it insitu.db bash
        psql -U [psql_username] [psql_database] < create_views.sql

1. Create elasticsearch index and start the development server:

        python manage.py search_index -f --rebuild
        python manage.py runserver 0.0.0.0:8000

1. Run tests:

        docker exec -it insitu.app sh
        python manage.py test --settings=copernicus.test_settings

1. Check coverage:

        docker exec -it insitu.app sh
        coverage run --source='.' ./manage.py test --settings=copernicus.test_settings
        python coverage html

1. See it in action: <http://localhost:8000>

### Upgrading the application

1. Get the latest version of source code:

        cd copernicus-insitu-db
        git pull origin master

1. Update the application stack, all services should be "Up":

        docker-compose pull
        docker-compose up -d
        docker-compose ps

1. See it in action: <http://localhost:8000>

### Debugging

Customize docker orchestration for local development:

        cp docker-compose.override.yml.example docker-compose.override.yml

* Please make sure that `DEBUG = True` in the settings.

* Update docker-compose.override.yml file `app` section with the following so that `docker-entrypoint.sh` is not executed:

        entrypoint: ["/usr/bin/tail", "-f", "/dev/null"]

* Attach to docker container and start the server in debug mode:

        docker exec -it insitu.app sh
        python manage.py runserver 0.0.0.0:8000

* See it in action: <http://localhost:8000>

## Set User roles

* Read-Only User
  - create a new regular user and add the user group "ReadOnly"
* ProductEditor
  - create a new regular user and add the user group "ProductEditor"
* PicklistsEditor
  - create a new staff user and add the user group "PicklistsEditor"

## Ubuntu elasticsearch container error

* If your host runs ubuntu your elasticsearch container may fail to run with the error "bootstrap checks failed". This happens because max map count is set under the value __262144__
* You can fix this temporarily(till you restart your machine) by running:

        sudo sysctl -w vm.max_map_count=262144

* You can fix this permanently by modifying your max_map_count file:

        sudo vim /proc/sys/vm/max_map_count
        # Change the value from the file with 262144 and save

# Save to fixtures explorer queries

        python manage.py dumpdata explorer.query > explorer.json

To install
# Generate Sphinx documentation

        cd docs/
        make html

After the documentation has changed, a new PDF file should be generated and it should replace the current file.

        docker exec -it insitu.app sh
        apk add texlive-full
        cd docs/
        make latexpdf
        cp _build/latex/CIS2.pdf ../insitu/static/docs/CIS2.pdf
        
        
        
