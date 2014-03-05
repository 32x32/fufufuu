from django.conf.urls import patterns, url
from fufufuu.flat.views import FlatMarkdownView, FlatHelpView


urlpatterns = patterns('',

    url(r'^help/$',             FlatHelpView.as_view(), name='flat.help'),
    url(r'^markdown/$',         FlatMarkdownView.as_view(), name='flat.markdown'),

)
