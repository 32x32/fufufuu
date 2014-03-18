import os
from fufufuu.core.logging import email_admin_limit

DEBUG = False
DEBUG_TOOLBAR = False
DEBUG_TOOLBAR_PATCH_SETTINGS = False
TEMPLATE_DEBUG = DEBUG

#-------------------------------------------------------------------------------
# django settings
#-------------------------------------------------------------------------------

MEDIA_ROOT = '/var/www/fufufuu/media'
STATIC_ROOT = '/var/www/fufufuu/static'

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
    'beta.fufufuu.net',
]

SESSION_COOKIE_DOMAIN = 'beta.fufufuu.net'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

#-------------------------------------------------------------------------------
# custom settings
#-------------------------------------------------------------------------------

RESOURCE_VERSION = 'fabric:resource-version'

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
        'errors': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/www/fufufuu/logs/errors.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 30,
            'encoding': 'utf-8',
        },
    },

    # loggers
    'loggers': {
        '': {
            'handlers': ['email_admin', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['email_admin', 'errors'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
