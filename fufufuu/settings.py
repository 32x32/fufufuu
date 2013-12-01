import os
from django.utils.translation import ugettext, ungettext
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'jr!s(3kt-i)tk8qkn$phyt3itptg08vh8gzu=cs#z6otufv#y2'

DEBUG = False
DEBUG_TOOLBAR = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []
INTERNAL_IPS = ['127.0.0.1',]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'south',

    'fufufuu.core',
    'fufufuu.manga',
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

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'

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
TEMPLATE_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_DIRS),
    auto_reload=DEBUG,
    extensions=[
        'jinja2.ext.i18n',
        'jinja2.ext.with_',
        'fufufuu.core.jinja2htmlcompress.HTMLCompress',
    ],
)

TEMPLATE_ENV.install_gettext_callables(ugettext, ungettext)

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
