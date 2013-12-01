import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'jr!s(3kt-i)tk8qkn$phyt3itptg08vh8gzu=cs#z6otufv#y2'

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TIME_ZONE = 'UTC'
USE_TZ = True

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'
