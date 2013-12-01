import os, sys
sys.path.append('/var/www/fufufuu/django')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fufufuu.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
