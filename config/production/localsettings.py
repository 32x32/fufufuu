import os
import datetime

import pytz

from fufufuu.core.logging import email_admin_limit

DEBUG = False
DEBUG_TOOLBAR = False
DEBUG_TOOLBAR_PATCH_SETTINGS = False
TEMPLATE_DEBUG = DEBUG

RESOURCE_VERSION = 'fabric:resource-version'

#-------------------------------------------------------------------------------
# django settings
#-------------------------------------------------------------------------------

MEDIA_ROOT = '/var/www/fufufuu/media'

STATIC_ROOT = '/var/www/fufufuu/static/{}'.format(RESOURCE_VERSION)
STATIC_URL = '/static/{}/'.format(RESOURCE_VERSION)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fufufuu',
        'USER': 'fufufuu_user',
        'PASSWORD': os.environ.get('FUFUFUU_DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'no-reply@fufufuu.net'

ALLOWED_HOSTS = [
    'fufufuu.net',
]

SESSION_COOKIE_DOMAIN = 'fufufuu.net'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

#-------------------------------------------------------------------------------
# custom settings
#-------------------------------------------------------------------------------

X_ACCEL = True

#-------------------------------------------------------------------------------
# logging settings
#-------------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    # formatters
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    # filters
    'filters': {
        'email_admin_limit': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': email_admin_limit,
        }
    },

    # handlers
    'handlers': {
        'email_admin': {
            'level': 'ERROR',
            'filters': ['email_admin_limit'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'fufufuu': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/www/fufufuu/logs/fufufuu-{}.log'.format(datetime.datetime.now(tz=pytz.UTC).strftime('%Y%m%d')),
            'encoding': 'utf-8',
        },
    },

    # loggers
    'loggers': {
        '': {
            'handlers': ['fufufuu'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['email_admin', 'fufufuu'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
