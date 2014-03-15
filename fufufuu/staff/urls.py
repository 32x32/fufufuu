from django.conf.urls import patterns, url
from fufufuu.staff.views import StaffView


urlpatterns = patterns('',

    url(r'^$',              StaffView.as_view(), name='staff'),

)
