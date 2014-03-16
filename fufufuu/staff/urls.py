from django.conf.urls import patterns, url
from fufufuu.staff.views import StaffSiteMetricsView, StaffSiteSettingsView


urlpatterns = patterns('',

    url(r'^site/metrics/$',         StaffSiteMetricsView.as_view(), name='staff.site.metrics'),
    url(r'^site/settings/$',        StaffSiteSettingsView.as_view(), name='staff.site.settings'),

)
