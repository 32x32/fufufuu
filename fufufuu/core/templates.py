from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ungettext
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from fufufuu.settings import TEMPLATE_DIRS, DEBUG


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
TEMPLATE_ENV.globals.update(**{
    'url': reverse,
})
