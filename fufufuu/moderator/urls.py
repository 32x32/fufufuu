from django.conf.urls import patterns, url
from fufufuu.moderator.views import ModeratorDashboardView


urlpatterns = patterns('',

    url(r'^$',              ModeratorDashboardView.as_view(), name='moderator.dashboard'),

)
