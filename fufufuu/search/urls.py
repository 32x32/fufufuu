from django.conf.urls import patterns, url
from fufufuu.search.views import SearchView


urlpatterns = patterns('',

    url(r'^$',          SearchView.as_view(), name='search'),

)
