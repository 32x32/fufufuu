from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from fufufuu.account.models import User


class CommentManager(models.Manager):

    def filter_content_object(self, content_object):
        content_type = ContentType.objects.get_for_model(content_object)
        return self.get_queryset().filter(content_type=content_type, object_id=content_object.id)


class Comment(models.Model):

    content_type    = models.ForeignKey(ContentType)
    object_id       = models.PositiveIntegerField()
    content_object  = generic.GenericForeignKey('content_type', 'object_id')

    markdown        = models.TextField()
    html            = models.TextField()

    is_removed      = models.BooleanField(default=False)
    ip_address      = models.CharField(max_length=200, blank=True, null=True)

    created_by      = models.ForeignKey(User, related_name='+', blank=True, null=True, on_delete=models.SET_NULL)
    created_on      = models.DateTimeField(auto_now_add=True)

    objects         = CommentManager()

    class Meta:
        db_table = 'comment'
        index_together = [('content_type', 'object_id')]
