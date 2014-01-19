from django.conf.urls import patterns, include, url
from django.contrib import admin
from fufufuu.manga.views import MangaListView
from fufufuu.settings import DEBUG, MEDIA_ROOT

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$',                  MangaListView.as_view(), name='manga.list'),

    # apps
    url(r'^account/',           include('fufufuu.account.urls')),
    url(r'^download/',          include('fufufuu.download.urls')),
    url(r'^i18n/',              include('django.conf.urls.i18n')),
    url(r'^m/',                 include('fufufuu.manga.urls')),
    url(r'^tag/',               include('fufufuu.tag.urls')),
    url(r'^upload/',            include('fufufuu.upload.urls')),

)

if DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    )
