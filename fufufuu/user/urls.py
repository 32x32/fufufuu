from django.conf.urls import patterns, url
from fufufuu.user.views import UserView, UserUploadsView


urlpatterns = patterns('',

    url(r'^(?P<username>\w{4,20})/$',               UserView.as_view(), name='user'),
    url(r'^(?P<username>\w{4,20})/uploads/$',       UserUploadsView.as_view(), name='user.uploads'),

)
