from django.conf.urls import patterns, url
from fufufuu.legacy.views import LegacyTankListView, LegacyTankView


urlpatterns = patterns('',

    url(r'^tanks/$',                                    LegacyTankListView.as_view(), name='legacy.tank.list'),
    url(r'^tanks/(?P<id>\d+)/(?P<slug>[\w-]+)/$',       LegacyTankView.as_view(), name='legacy.tank'),

)
