FROM python:3.8-alpine

ARG REQFILE=requirements-dep.txt
ENV APP_HOME=/var/local/copernicus

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install --upgrade pip \
    && pip install Pillow \
    && apk del build-deps
RUN apk add --no-cache --update gcc netcat-openbsd postgresql-dev \
    pcre-dev musl-dev linux-headers make \
    xvfb  ttf-freefont fontconfig dbus qt5-qtbase-dev \
    qt5-qtwebkit-dev qt5-qtsvg-dev qt5-qtxmlpatterns-dev
RUN apk add qt5-qtbase-dev wkhtmltopdf --no-cache \
    --repository http://dl-3.alpinelinux.org/alpine/edge/community/ \
    --allow-untrusted

RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/logging

COPY . $APP_HOME
WORKDIR $APP_HOME

RUN pip install --no-cache-dir -r $REQFILE
RUN cd docs && make html

ENTRYPOINT ["./docker-entrypoint.sh"]
