from distutils.util import strtobool

from .base import *

DEBUG = True

MAX_DISTANCE_KM = 10 ** 6

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


def bool_(string):
    return bool(strtobool(string))


USE_GMAPS_API = get_env_variable('USE_GMAPS_API', default=False,
                                 raise_exception=False,
                                 type=bool_)
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
