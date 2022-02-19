#!/bin/bash
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

if [ "$APP_ENV" = "dev" ]
then
    python manage.py runserver 0.0.0.0:8000
    # daphne -b 0.0.0.0 -p 8000 collectorapp.asgi:application

elif [ "$APP_ENV" = "worker" ]
then
    celery -A collectorapp worker -c 1 & python manage.py runscript collect

else
    # gunicorn collectorapp.wsgi:application --bind 0.0.0.0:8000
    daphne -b 0.0.0.0 -p 8000 collectorapp.asgi:application
fi
