from django.conf.urls import patterns, url
from fufufuu.blog.views import BlogEntryListView, BlogEntryView, \
    BlogEntryCreateView, BlogEntryEditView


urlpatterns = patterns('',

    url(r'^$',                                      BlogEntryListView.as_view(), name='blog.entry.list'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$',         BlogEntryView.as_view(), name='blog.entry'),

    url(r'^new/$',                                  BlogEntryCreateView.as_view(), name='blog.entry.create'),
    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/edit/$',    BlogEntryEditView.as_view(), name='blog.entry.edit'),

)
