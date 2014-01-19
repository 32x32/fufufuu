from django.conf.urls import patterns, url
from fufufuu.download.views import DownloadView


urlpatterns = patterns('',

    url(r'^(?P<key>\w{64})/(?P<filename>.*)/$',     DownloadView.as_view(), name='download')

)
