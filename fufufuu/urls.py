from django.conf.urls import patterns, include, url
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page

from fufufuu.core.views import PageNotFoundView, ServerErrorView
from fufufuu.manga.views import MangaListView, MangaListFavoritesView
from fufufuu.settings import DEBUG, DEBUG_TOOLBAR_PATCH_SETTINGS, MEDIA_ROOT
from fufufuu.sitemaps import SITEMAPS


handler404 = PageNotFoundView.as_view()
handler500 = ServerErrorView.as_view()


urlpatterns = patterns('',

    url(r'^$',                          MangaListView.as_view(), name='manga.list'),

    # apps
    url(r'^account/',                   include('fufufuu.account.urls')),
    url(r'^captcha/',                   include('captcha.urls')),
    url(r'^download/',                  include('fufufuu.download.urls')),
    url(r'^f/',                         include('fufufuu.flat.urls')),
    url(r'^i18n/',                      include('django.conf.urls.i18n')),
    url(r'^m/',                         include('fufufuu.manga.urls')),
    url(r'^search/',                    include('fufufuu.search.urls')),
    url(r'^staff/',                     include('fufufuu.staff.urls')),
    url(r'^tag/',                       include('fufufuu.tag.urls')),
    url(r'^u/',                         include('fufufuu.user.urls')),
    url(r'^upload/',                    include('fufufuu.upload.urls')),

    # individual views
    url(r'^favorites/$',                MangaListFavoritesView.as_view(), name='manga.list.favorites'),

    # sitemap
    url(r'^sitemap\.xml$',              cache_page(60*60)(sitemap), {'sitemaps': SITEMAPS}, name='sitemap'),

    # legacy urls
    url(r'^',                           include('fufufuu.legacy.urls')),

)

#-------------------------------------------------------------------------------
# debug specific settings
#-------------------------------------------------------------------------------

if DEBUG:
    urlpatterns += patterns('',
        url(r'^media/image/',           include('fufufuu.image.urls')),
        url(r'^media/(?P<path>.*)$',    'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    )

if DEBUG and not DEBUG_TOOLBAR_PATCH_SETTINGS:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/',             include(debug_toolbar.urls)),
    )
