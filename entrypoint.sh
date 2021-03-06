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

    if [ "X$DJANGO_RECREATE_TEST_DATA" = 'Xyes' ]; then
        echo "clearing data from the database"
        python manage.py flush --noinput
        echo "populating the database"
        python manage.py populate_db
    fi

    echo "creating agreements"
    python manage.py create_agreements
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
    python manage.py create_superuser --username  ${ADMIN_USERNAME} --password  ${ADMIN_PASSWORD}
fi
exec "$@"