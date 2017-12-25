from .base import *

DEBUG = False
ENABLE_SMS_CONFIRMATION = True
USE_GMAPS_API = True
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
        'ATOMIC_REQUESTS': True
    }
}
