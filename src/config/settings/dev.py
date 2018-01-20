from .base import *

DEBUG = True

MAX_DISTANCE_KM = 10 ** 6

# TODO temporary stub
ALLOWED_HOSTS = ['dev.4hands2go.bigblackbug.me', '35.195.99.19']

FCM_DJANGO_SETTINGS = {
    'FCM_SERVER_KEY': "AAAAn_i-bL4:APA91bHJj5gX88W-dMy-u_3JDUf1oSqmp0VOGP8qkl"
                      "INUegqX2ZavfVg4clL5zfMOshPkr7AODpX8yhmphhsSACPAUxJeZJ7"
                      "U3E0Fwua4F-8RPYBx5DuE778lYkPvPH7e4MjQzgVY75p",
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
