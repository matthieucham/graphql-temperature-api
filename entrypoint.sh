#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput --clear

# start feed consumer in background
echo "Start consume_feed"
python manage.py consume_feed 1 &
echo "consume_feed started in background"

exec "$@"