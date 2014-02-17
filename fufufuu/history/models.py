from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from fufufuu.account.models import User


class History(models.Model):

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'history'
        index_together = [('content_type', 'object_id')]


class HistoryField(models.Model):

    history = models.ForeignKey(History, on_delete=models.CASCADE)
    field = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()

    class Meta:
        db_table = 'history_field'
