from django.conf.urls import patterns, url
from fufufuu.tag.views import TagListView


urlpatterns = patterns('',

    url(r'^(?P<tag_type>\w+)/$',    TagListView.as_view(), name='tag.list'),

)
