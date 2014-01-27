import json
import mimetypes
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse
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
            disposition='attachment' if attachment else 'inline',
            filename=filename,
        )
