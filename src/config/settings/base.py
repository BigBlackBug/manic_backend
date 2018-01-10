"""
Django settings for _4hands2go project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from django.core.exceptions import ImproperlyConfigured
from unipath import Path


def get_env_variable(var_name, raise_exception=True, default=None, type=str):
    """Get the environment variable or raise exception."""
    try:
        return type(os.environ[var_name])
    except KeyError:
        if raise_exception:
            error_msg = "Set the {} environment variable".format(var_name)
            raise ImproperlyConfigured(error_msg)
        else:
            return default
    except TypeError:
        raise ImproperlyConfigured('Unexpected Value Type')


BASE_DIR = Path(__file__).ancestor(3)

# TODO really? the slash did it!
MEDIA_ROOT = BASE_DIR.ancestor(1).child("media") + '/'
MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR.ancestor(1).child("static") + '/'
STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     BASE_DIR.ancestor(1).child("static"),
# )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# TODO do smth about SECRET_KEY
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0n#gk&((m1y4crfx6hv-5_!$g0@g+*d_r&(e6^259arysd2wm='

# TODO move this to env vars
GMAPS_API_KEY = 'AIzaSyBoKNDWTb5XPdY4k1Wx0kQDpZDm0GW0FTc'
SMS_API_KEY = '492B4520-D0A7-C70D-628A-7F4B858671CD'
CLOUDPAYMENTS_PUBLIC_ID = 'pk_60c4e78f074563b799b61b0d36019'
CLOUDPAYMENTS_API_SECRET = '5e9fb61716880f83b91a6ed928718baf'

# Application settings
ORDER_CANCELLATION_WINDOW_HOURS = 3
MAX_DISTANCE_KM = 20.0
USE_GMAPS_API = False
ENABLE_SMS_CONFIRMATION = False
MINIMUM_BALANCE = 500

ADMIN_APP_USER_MODEL = 'auth.User'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'src.apps.core',
    'src.apps.categories',
    'src.apps.authentication',
    'src.apps.masters',
    'src.apps.clients',
    'src.apps.orders',
    'src.apps.finances',
    'src.apps.devices',
    'src.utils.admin_commands',

    'rest_framework',
    'rest_framework_swagger',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'src.apps.authentication.backend.TokenAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': 'src.apps.core.utils.custom_exception_handler'
}

SWAGGER_SETTINGS = {
    'DOC_EXPANSION': 'list'
}

FCM_DJANGO_SETTINGS = {
    'FCM_SERVER_KEY': None,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (BASE_DIR.child('templates'),)
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.ancestor(1).child('db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# TODO process logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)-8s] '
                      '[%(message)s] [%(name)s:%(lineno)s - %(funcName)s()]'
        },
        'simple': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'error_console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'warning_email': {
            'level': 'WARNING',
            # TODO email handler
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'src.apps': {
            'level': 'DEBUG',
            'handlers': ['console', 'error_console'],
            'propagate': False
        },

    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    }
}
