from .base import *

DEBUG = True

MAX_DISTANCE_KM = 10 ** 6

# TODO temporary stub
ALLOWED_HOSTS = ['dev.4hands2go.bigblackbug.me', '35.195.99.19']

FCM_DJANGO_SETTINGS = {
    'FCM_SERVER_KEY': "AAAA9VT8jq4:APA91bErqX4Ul10NURZcVXKohbXaif1lx96Er2QVSlj"
                      "PNKla55NZRBQrE1-W8RQOpCVQN_Olnvql1RohjsIAwAd5BXVFqYiGd4"
                      "36m7KNgOBuwklg4uuctbBr2yY1joxBSp4YGir39qGS",
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
