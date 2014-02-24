from django.conf.urls import patterns, url
from fufufuu.flat.views import FlatMarkdownView


urlpatterns = patterns('',

    url(r'^markdown/$',         FlatMarkdownView.as_view(), name='flat.markdown'),

)
