#!/bin/bash
set -e

if [[ ${DATABASE_URL} ]]; then
    echo "${DATABASE_URL} is set"
    until psql $DATABASE_URL -c '\l'; do
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 1
    done
    >&2 echo "Postgres is up - continuing"
fi

if [ "X$DJANGO_RUN_MIGRATIONS" = 'Xyes' ]; then
    echo "running migrations"
    python manage.py migrate --noinput
fi

if [ "X$DJANGO_RUN_COLLECTSTATIC" = 'Xyes' ]; then
    echo "collecting static"
    python manage.py collectstatic --noinput
fi

exec "$@"