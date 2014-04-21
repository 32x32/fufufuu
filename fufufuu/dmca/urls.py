from django.conf.urls import patterns, url
from fufufuu.dmca.views import DmcaListView


urlpatterns = patterns('',

    url(r'^$',      DmcaListView.as_view(), name='dmca.list'),

)
