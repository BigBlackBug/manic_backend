#!/bin/sh
set -e

if [ "X$DJANGO_RUN_MIGRATIONS" = 'Xyes' ]; then
    echo "running migrations"
    python manage.py migrate --noinput
fi

#if [ "X$DJANGO_RUN_COLLECTSTATIC" = 'Xyes' ]; then
#    python manage.py collectstatic --noinput
#fi

exec "$@"