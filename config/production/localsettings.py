import os

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
MD2HTML = '/usr/bin/md2html'
