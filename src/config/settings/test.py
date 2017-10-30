from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '4hands2go_local',
        'USER': '4hands2go_local',
        'PASSWORD': '4hands2go_local',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
