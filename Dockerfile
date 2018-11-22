FROM python:3.6-alpine

ARG REQFILE=requirements-dep.txt
ENV APP_HOME=/var/local/copernicus

RUN apk add --no-cache --update gcc netcat-openbsd postgresql-dev \
                                pcre-dev musl-dev linux-headers make \
                                xvfb  ttf-freefont fontconfig dbus
RUN apk add qt5-qtbase-dev wkhtmltopdf --no-cache \
            --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ \
            --allow-untrusted

RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/logging

COPY requirements* $APP_HOME/
WORKDIR $APP_HOME

RUN pip install --no-cache-dir  -r $REQFILE

COPY . $APP_HOME
RUN cd docs && make html

ENTRYPOINT ["./docker-entrypoint.sh"]
