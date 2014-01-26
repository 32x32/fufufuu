from django.conf.urls import patterns, url
from fufufuu.image.views import ImageView


urlpatterns = patterns('',

    url(r'^(?P<key_type>\w+)/.*/(?P<key_id>\w+)-\w+.jpg$',      ImageView.as_view(), name='image'),

)