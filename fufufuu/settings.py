import os
from fufufuu.core.languages import Language

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'jr!s(3kt-i)tk8qkn$phyt3itptg08vh8gzu=cs#z6otufv#y2'

DEBUG = False
DEBUG_TOOLBAR = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Derek Kwok', 'derek.kai.chun.kwok@gmail.com'),
)

ALLOWED_HOSTS = []
INTERNAL_IPS = ['127.0.0.1',]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'captcha',
    'south',

    'fufufuu.account',
    'fufufuu.core',
    'fufufuu.download',
    'fufufuu.image',
    'fufufuu.manga',
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
STATIC_URL = '/static/'
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

X_ACCEL = False

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
    'django.contrib.messages.context_processors.messages'
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
