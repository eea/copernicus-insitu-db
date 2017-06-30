# copernicus-insitu-db
Copernicus In Situ Component Information System

## Prerequisites

* Install [Docker](https://www.docker.com)
* Install [Docker Compose](https://docs.docker.com/compose/)

## Installation

### Production

TO DO

### Development

1. Clone the repository:

  ```
  $ git clone https://github.com/eea/copernicus-insitu-db.git
  $ cd copernicus-insitu-db
  ```

2. Create a local build:

  ```
  $ docker build -t insitu:devel .
  ```

3. Create and fill in the configuration files:

  ```
  $ cd env/
  $ cp app.env.example app.env
  $ cp postgres.env.example postgres.env
  ```

4. Create a `docker-compose.yml` file similar to [this example](https://gist.github.com/iuliachiriac/638e7f33b19368133a3fb6d815f44bac).

5. Start stack:

  ```
  $ docker-compose up -d
  ```

6. Run migrations, create elasticsearch index, and start the development server:

  ```
  $ docker exec -it insitu_app bash
  $ pip install -r requirements-dev.txt
  $ ./manage.py migrate
  $ ./manage.py loaddata picklists
  $ ./manage.py search_index --rebuild
  $ ./manage.py runserver 0.0.0.0:8000
  ```

7. Visit [http://localhost:8000/](http://localhost:8000/) to see if the app is up and running.

### Running tests

1. Run tests:

    ```
    $ ./manage.py test --settings=copernicus.testsettings
    ```

2. Check coverage:

    ```
    $ coverage run --source='.' ./manage.py test --settings=copernicus.testsettings
    $ coverage html
    ```
