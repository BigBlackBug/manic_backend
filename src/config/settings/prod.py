from .base import *

DEBUG = False

MAX_DISTANCE_KM = 20

ALLOWED_HOSTS = ['*']

FCM_DJANGO_SETTINGS = {
    'FCM_SERVER_KEY': get_env_variable('FCM_SERVER_KEY')
}

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
