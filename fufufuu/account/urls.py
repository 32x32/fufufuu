from django.conf.urls import patterns, url
from fufufuu.account.views import AccountLoginView, AccountLogoutView, AccountRegisterView


urlpatterns = patterns('',

    url(r'^login/$',        AccountLoginView.as_view(), name='account.login'),
    url(r'^register/$',     AccountRegisterView.as_view(), name='account.register'),
    url(r'^logout/$',       AccountLogoutView.as_view(), name='account.logout'),

)
