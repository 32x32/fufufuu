from django.conf.urls import patterns, url
from fufufuu.comment.views import CommentPostView


urlpatterns = patterns('',

    url(r'^post/$',         CommentPostView.as_view(), name='comment.post'),

)
