from django.conf.urls import patterns, url
from fufufuu.upload.views import UploadListView


urlpatterns = patterns('',

    url(r'^$',          UploadListView.as_view(), name='upload.list'),

)
