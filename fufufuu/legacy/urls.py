from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from fufufuu.legacy.views import LegacyTankView


urlpatterns = patterns('',

    url(r'^help/$',                                     RedirectView.as_view(url=reverse_lazy('flat.help')), name='legacy.help'),
    url(r'^tanks/$',                                    RedirectView.as_view(url=reverse_lazy('tag.list.grid.tank')), name='legacy.tank.list'),
    url(r'^tanks/(?P<id>\d+)/(?P<slug>[\w-]+)/$',       LegacyTankView.as_view(), name='legacy.tank'),

)
