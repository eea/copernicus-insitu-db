FROM python:3.8-alpine
ARG REQFILE=requirements-dep.txt
ENV APP_HOME=/var/local/copernicus


COPY . $APP_HOME
WORKDIR $APP_HOME


RUN apk update \
    && apk add --no-cache python3-dev musl-dev \
        jpeg-dev zlib-dev libjpeg \
        gcc netcat-openbsd postgresql-dev \
    pcre-dev linux-headers make \
    xvfb  ttf-freefont fontconfig dbus libffi-dev \
    --repository http://dl-3.alpinelinux.org/alpine/edge/community/ \
    --allow-untrusted \ 
    && mkdir -p $APP_HOME/logging \

    && pip install pip==24.0 \
    && pip install Pillow \
    && pip install --no-cache-dir -r $REQFILE \

    && cd docs \
    && make html

ENTRYPOINT ["./docker-entrypoint.sh"]
