from django.conf.urls import patterns, include, url
from django.contrib import admin
from fufufuu.manga.views import MangaListView

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$',                  MangaListView.as_view(), name='manga.list'),

    # apps
    url(r'^account/',           include('fufufuu.account.urls')),
    url(r'^admin/',             include(admin.site.urls)),
    url(r'^i18n/',              include('django.conf.urls.i18n')),
    url(r'^tag/',               include('fufufuu.tag.urls')),

)
