from django.conf.urls import patterns, url
from fufufuu.manga.views import MangaView, MangaEditView, MangaEditImagesView, MangaHistoryView


urlpatterns = patterns('',

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$',                 MangaView.as_view(), name='manga'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/edit/$',            MangaEditView.as_view(), name='manga.edit'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/edit/images/$',     MangaEditImagesView.as_view(), name='manga.edit.images'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/history/$',         MangaHistoryView.as_view(), name='manga.history'),

)
