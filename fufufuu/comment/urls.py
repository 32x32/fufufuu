from django.conf.urls import patterns, url
from fufufuu.comment.views import CommentPostView, CommentDeleteView


urlpatterns = patterns('',

    url(r'^post/$',                     CommentPostView.as_view(), name='comment.post'),
    url(r'^(?P<id>\d+)/delete/$',       CommentDeleteView.as_view(), name='comment.delete'),

)
