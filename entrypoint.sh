#!/bin/sh
set -e

until psql $DATABASE_URL -c '\l'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing"

if [ "X$DJANGO_RUN_MIGRATIONS" = 'Xyes' ]; then
    echo "running migrations"
    python manage.py migrate --noinput
fi

#if [ "X$DJANGO_RUN_COLLECTSTATIC" = 'Xyes' ]; then
#    python manage.py collectstatic --noinput
#fi

exec "$@"