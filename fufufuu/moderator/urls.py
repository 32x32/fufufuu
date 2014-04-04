from django.conf.urls import patterns, url
from fufufuu.moderator.views import ModeratorReportMangaListView, ModeratorReportMangaView


urlpatterns = patterns('',

    url(r'^report/manga/$',                 ModeratorReportMangaListView.as_view(), name='moderator.report.manga.list'),
    url(r'^report/manga/(?P<id>\d+)/$',     ModeratorReportMangaView.as_view(), name='moderator.report.manga'),

)
