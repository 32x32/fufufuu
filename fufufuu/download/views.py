from django.shortcuts import get_object_or_404
from fufufuu.core.response import HttpResponseXAccel
from fufufuu.core.views import TemplateView
from fufufuu.download.models import DownloadLink


class DownloadView(TemplateView):

    def get(self, request, key, filename):
        download = get_object_or_404(DownloadLink, key=key)
        return HttpResponseXAccel(url=download.url, filename=filename)
