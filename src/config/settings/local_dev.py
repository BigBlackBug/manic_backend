from distutils.util import strtobool

from .base import *


def bool_(string):
    return bool(strtobool(string))


DEBUG = True

MAX_DISTANCE_KM = 10 ** 6
USE_GMAPS_API = get_env_variable('USE_GMAPS_API', default=False,
                                 raise_exception=False,
                                 type=bool_)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '4hands2go_local',
        'USER': '4hands2go_local',
        'PASSWORD': '4hands2go_local',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True
    }
}
