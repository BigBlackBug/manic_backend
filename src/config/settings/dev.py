from .base import *

DEBUG = True

# TODO temporary stub
ALLOWED_HOSTS = ['dev.4hands2go.bigblackbug.me', '35.195.227.131']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('DATABASE_NAME'),
        'USER': get_env_variable('DATABASE_USER'),
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': get_env_variable('DATABASE_HOST'),
        'PORT': '5432',
    }
}
