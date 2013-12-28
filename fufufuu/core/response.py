import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse


class HttpResponseJson(HttpResponse):

    def __init__(self, content=None, status_code=200):
        super(HttpResponseJson, self).__init__(
            content=json.dumps(content, cls=DjangoJSONEncoder),
            content_type='application/json',
        )
        self['Cache-Control'] = 'private; max-age=30'
        self.status_code = status_code


# class HttpResponseXAccel(HttpResponse):
#     """
#     This is an Nginx specific response using header 'X-Accel-Redirect'. This
#     response will serve static files that are normally protected.
#
#     The "file" parameter must implemented the url property:
#
#         "file.url"      --> returns the media url
#
#     Regular models.FileField fields will have the above automatically
#     implemented.
#     """
#
#     def __init__(self, file, content_type=None, attachment=False):
#         super(HttpResponseXAccel, self).__init__(content_type=content_type)
#
#         if X_ACCEL:
#             self['X-Accel-Redirect'] = file.url
#         else:
#             self.status_code = 302
#             self['Location'] = file.url
#
#         if attachment:
#             self['Content-Disposition'] = 'attachment;'
#         else:
#             self['Content-Disposition'] = 'inline;'
