import os

DEBUG = True
DEBUG_TOOLBAR = True
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
    'staging.fufufuu.net',
]
INTERNAL_IPS = [
    '108.162.173.189',
]

SESSION_COOKIE_DOMAIN = 'staging.fufufuu.net'

#-------------------------------------------------------------------------------
# custom settings
#-------------------------------------------------------------------------------

RESOURCE_VERSION = 'fabric:resource-version'

X_ACCEL = True
MD2HTML = '/usr/bin/md2html'
