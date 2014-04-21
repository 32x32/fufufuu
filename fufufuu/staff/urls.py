from django.conf.urls import patterns, url
from fufufuu.staff.views import StaffSiteMetricsView, StaffSiteSettingsView, \
    StaffDmcaAccountListView, StaffDmcaAccountView


urlpatterns = patterns('',

    url(r'^site/metrics/$',                 StaffSiteMetricsView.as_view(), name='staff.site.metrics'),
    url(r'^site/settings/$',                StaffSiteSettingsView.as_view(), name='staff.site.settings'),

    url(r'^dmca/accounts/$',                StaffDmcaAccountListView.as_view(), name='staff.dmca.account.list'),
    url(r'^dmca/accounts/(?P<id>\d+)/$',    StaffDmcaAccountView.as_view(), name='staff.dmca.account'),

)
