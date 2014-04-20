import os
from fufufuu.core.languages import Language

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'jr!s(3kt-i)tk8qkn$phyt3itptg08vh8gzu=cs#z6otufv#y2'

DEBUG = False
DEBUG_TOOLBAR = False
DEBUG_TOOLBAR_PATCH_SETTINGS = True
TEMPLATE_DEBUG = DEBUG

RESOURCE_VERSION = 'development'

ADMINS = (
    ('Derek Kwok', 'derek.kai.chun.kwok@gmail.com'),
)

ALLOWED_HOSTS = []
INTERNAL_IPS = ['127.0.0.1',]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'captcha',
    'haystack',
    'south',

    'fufufuu.account',
    'fufufuu.blog',
    'fufufuu.comment',
    'fufufuu.core',
    'fufufuu.dmca',
    'fufufuu.download',
    'fufufuu.flat',
    'fufufuu.image',
    'fufufuu.legacy',
    'fufufuu.manga',
    'fufufuu.moderator',
    'fufufuu.report',
    'fufufuu.search',
    'fufufuu.staff',
    'fufufuu.tag',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'fufufuu.urls'
WSGI_APPLICATION = 'fufufuu.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'fufufuu.sqlite3'),
    }
}

TIME_ZONE = 'UTC'
USE_TZ = True

LANGUAGE_CODE = 'en'
LANGUAGES = Language.choices
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = ''
STATIC_URL = '/static/{}/'.format(RESOURCE_VERSION)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEST_RUNNER = 'fufufuu.core.tests.FufufuuTestSuiteRunner'

AUTH_USER_MODEL = 'account.User'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

DEFAULT_FILE_STORAGE = 'fufufuu.core.storage.FufufuuStorage'

#-------------------------------------------------------------------------------
# miscellaneous settings
#-------------------------------------------------------------------------------

X_ACCEL = False

MAX_TOTAL_SIZE          = 200 * 1024 * 1024
MAX_IMAGE_FILE_SIZE     = 8 * 1024 * 1024
MAX_IMAGE_DIMENSION     = (8000, 8000)
SUPPORTED_IMAGE_FORMATS = ['JPEG', 'PNG']

#-------------------------------------------------------------------------------
# captcha settings
#-------------------------------------------------------------------------------

CAPTCHA_FONT_SIZE = 30
CAPTCHA_LENGTH = 7

#-------------------------------------------------------------------------------
# cache settings
#-------------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

#-------------------------------------------------------------------------------
# default email settings
#-------------------------------------------------------------------------------

EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

DEFAULT_FROM_EMAIL = ''

#-------------------------------------------------------------------------------
# search settings
#-------------------------------------------------------------------------------

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'fufufuu',
    },
}

#-------------------------------------------------------------------------------
# template settings
#-------------------------------------------------------------------------------

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',
    'fufufuu.core.context_processors.resource_version',
    'fufufuu.core.context_processors.site_settings',
)

#-------------------------------------------------------------------------------
# localsettings.py
#-------------------------------------------------------------------------------

try:
    from fufufuu.localsettings import *
except ImportError:
    pass

#-------------------------------------------------------------------------------
# see if we need to import debug toolbar
#-------------------------------------------------------------------------------

if DEBUG_TOOLBAR:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
