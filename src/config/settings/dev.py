from .base import *

DEBUG = True

MAX_DISTANCE_KM = 10 ** 6
USE_GMAPS_API = get_env_variable('USE_GMAPS_API', default=True)
# TODO temporary stub
ALLOWED_HOSTS = ['dev.4hands2go.bigblackbug.me', '35.195.99.19']

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
