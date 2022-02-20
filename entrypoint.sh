#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput --clear

# start feed consumer
python manage.py consume_feed

exec "$@"