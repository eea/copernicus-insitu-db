FROM python:3.8-slim

ARG REQFILE=requirements-dep.txt
ENV APP_HOME=/var/local/copernicus

COPY . $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    cron \
    libcairo2-dev \
    libffi-dev \
    libjpeg62-turbo \
    libpango1.0-dev \
    libxml2-dev \
    libxslt1-dev \
    netcat-traditional \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p $APP_HOME/logging

RUN pip install pip==24.0 && \
    pip install --no-cache-dir -r $REQFILE

RUN cd docs && make html

ENTRYPOINT ["./docker-entrypoint.sh"]
