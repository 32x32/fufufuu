from django.db import models
from fufufuu.account.models import User


class SiteSetting(models.Model):

    key = models.CharField(max_length=255)
    val = models.CharField(max_length=255)

    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'site_setting'
