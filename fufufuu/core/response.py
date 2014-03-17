import json
import mimetypes
import sys
from email.header import Header

from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse, BadHeaderError
from django.utils import six

from fufufuu.settings import X_ACCEL


class HttpResponseJson(HttpResponse):

    def __init__(self, content=None, status_code=200):
        super(HttpResponseJson, self).__init__(
            content=json.dumps(content, cls=DjangoJSONEncoder),
            content_type='application/json',
        )
        self['Cache-Control'] = 'private; max-age=30'
        self.status_code = status_code


class HttpResponseXAccel(HttpResponse):
    """
    This is an Nginx specific response using header 'X-Accel-Redirect'. This
    response should be used to serve static files that are normally protected.
    """

    def __init__(self, url, filename, attachment=True):
        super(HttpResponseXAccel, self).__init__(content_type=mimetypes.guess_type(url)[0])

        if X_ACCEL:
            self['X-Accel-Redirect'] = url
            self['X-Accel-Limit-Rate'] = 1 * 1024 * 1024
        else:
            self.status_code = 302
            self['Location'] = url

        self['Content-Disposition'] = '{disposition}; filename="{filename}"'.format(
            disposition=attachment and 'attachment' or 'inline',
            filename=filename,
        )

    def _convert_to_charset(self, value, charset, mime_encode=False):
        """Converts headers key/value to ascii/latin-1 native strings.

        `charset` must be 'ascii' or 'latin-1'. If `mime_encode` is True and
        `value` value can't be represented in the given charset, MIME-encoding
        is applied.
        """
        if not isinstance(value, (bytes, six.text_type)):
            value = str(value)
        try:
            if six.PY3:
                if isinstance(value, str):
                    # Ensure string is valid in given charset
                    value.encode(charset)
                else:
                    # Convert bytestring using given charset
                    value = value.decode(charset)
            else:
                if isinstance(value, str):
                    # Ensure string is valid in given charset
                    value.decode(charset)
                else:
                    # Convert unicode string to given charset
                    value = value.encode(charset)
        except UnicodeError as e:
            if mime_encode:
                # Wrapping in str() is a workaround for #12422 under Python 2.
                value = str(Header(value, 'utf-8', maxlinelen=sys.maxsize).encode())
            else:
                e.reason += ', HTTP response headers must be in %s format' % charset
                raise
        if str('\n') in value or str('\r') in value:
            raise BadHeaderError("Header values can't contain newlines (got %r)" % value)
        return value
