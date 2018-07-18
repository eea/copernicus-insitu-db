FROM python:3.6-alpine

ARG REQFILE=requirements-dep.txt
ENV APP_HOME=/var/local/copernicus

RUN apk add --no-cache --update gcc netcat-openbsd postgresql-dev pcre-dev musl-dev linux-headers

RUN mkdir -p $APP_HOME \
    && mkdir -p /var/local/static/protected

COPY requirements* $APP_HOME/
WORKDIR $APP_HOME

RUN pip install --no-cache-dir  -r $REQFILE

COPY . $APP_HOME

ENTRYPOINT ["./docker-entrypoint.sh"]
