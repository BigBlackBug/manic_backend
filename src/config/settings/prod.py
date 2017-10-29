from .base import *

DEBUG = False

# TODO temporary stub
ALLOWED_HOSTS = ['4hands2go.bigblackbug.me', '35.195.99.19']

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
