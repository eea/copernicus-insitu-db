FROM python:3.6-slim
LABEL maintainer="European Environment Agency (EEA): IDM2 S-Team"

ENV PROJ_DIR=/var/local/copernicus

RUN runDeps="vim netcat libpq-dev" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*


RUN mkdir -p $PROJ_DIR
COPY . $PROJ_DIR
WORKDIR $PROJ_DIR

RUN pip install -r requirements-dep.txt

ENTRYPOINT ["./docker-entrypoint.sh"]
