# pull official base image
FROM python:3.8-slim-buster

ENV APP_RUN=app
ENV APP_USER=gunicorn
ENV APP_PATH=/app

COPY requirements.txt /

RUN echo -n \
    && mkdir $APP_PATH $APP_PATH/staticfiles /creds \
    && useradd --system --shell /bin/true --home $APP_PATH $APP_USER \
    && chown -R $APP_USER:$APP_USER /creds \
    && chown -R $APP_USER:$APP_USER $APP_PATH \
    && apt-get update \
    && apt-get -y install --no-install-recommends \
    libpq5 \
    build-essential \
    libpq-dev \
    && python -m pip install -r /requirements.txt \
    && rm -f /requirements.txt \
    && apt-get -y remove \
    build-essential \
    libpq-dev \
    && apt-get -y autopurge \
    && rm -rf /var/lib/apt/lists/*

# copy project
COPY backend/ $APP_PATH/

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_PATH/entrypoint.sh
RUN chmod +x $APP_PATH/entrypoint.sh

USER $APP_USER
WORKDIR $APP_PATH

ENTRYPOINT ["/app/entrypoint.sh" ]
