from django.conf.urls import patterns, url
from fufufuu.manga.views import *


urlpatterns = patterns('',

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$',                 MangaInfoView.as_view(), name='manga.info'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/read/$',            MangaView.as_view(), name='manga'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/thumbs/$',          MangaThumbnailsView.as_view(), name='manga.thumbnails'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/comments/$',        MangaCommentsView.as_view(), name='manga.comments'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/download/$',        MangaDownloadView.as_view(), name='manga.download'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/favorite/$',        MangaFavoriteView.as_view(), name='manga.favorite'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/report/$',          MangaReportView.as_view(), name='manga.report'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/revisions/$',       MangaRevisionsView.as_view(), name='manga.revisions'),

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/edit/$',            MangaEditView.as_view(), name='manga.edit'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/edit/images/$',     MangaEditImagesView.as_view(), name='manga.edit.images'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/edit/upload/$',     MangaEditUploadView.as_view(), name='manga.edit.upload'),

)
