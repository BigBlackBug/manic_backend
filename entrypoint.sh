#!/bin/bash
set -x

if [[ ${DATABASE_HOST} ]]; then
    export PGPASSWORD=${DATABASE_PASSWORD}
    until psql -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME -c '\l'; do
      >&2 echo "Postgres is unavailable - sleeping"
      sleep 1
    done
    >&2 echo "Postgres is up - continuing"
    psql -h $DATABASE_HOST -U $DATABASE_USER -d template1 -c 'create extension hstore;'
    unset PGPASSWORD
fi

set -e

if [ "X$DJANGO_RUN_MIGRATIONS" = 'Xyes' ]; then
    echo "running migrations"
    python manage.py migrate --noinput
fi

if [ "X$DJANGO_RUN_COLLECTSTATIC" = 'Xyes' ]; then
    echo "collecting static files"
    python manage.py collectstatic --noinput
fi

if [ "X$DJANGO_RUN_CREATESUPERUSER" = 'Xyes' ]; then
    echo "creating a superuser"
    if [ -z ${ADMIN_USERNAME+x} ]; then
        echo "Please set the ADMIN_USERNAME env variable";
        exit 1
    fi

    if [ -z ${ADMIN_PASSWORD+x} ]; then
        echo "Please set the ADMIN_PASSWORD env variable";
        exit 1
    fi
    ADMIN_EMAIL=admin@example.com
    python manage.py shell -c "from django.contrib.auth.models import User;\
      User.objects.filter(email='$ADMIN_EMAIL').delete();\
      User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')"
fi

exec "$@"