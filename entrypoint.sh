#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py collectstatic --noinput --clear

# start feed consumer in background
echo "Start consume_feed"
python manage.py consume_feed 1 &
echo "consume_feed started in background"

exec "$@"