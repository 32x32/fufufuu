from django.conf.urls import patterns, url
from fufufuu.moderator.views import ModeratorReportMangaListView


urlpatterns = patterns('',

    url(r'^report/manga/$',     ModeratorReportMangaListView.as_view(), name='moderator.report.manga.list'),

)
