import os
import binascii
from django.db import models
from fufufuu.account.models import User


class DownloadLink(models.Model):

    key = models.CharField(max_length=64, unique=True)
    url = models.CharField(max_length=1024)
    ip_address = models.CharField(max_length=200, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        self.key = binascii.hexlify(os.urandom(32)).decode('utf-8')
        super(DownloadLink, self).save(*args, **kwargs)

    class Meta:
        db_table = 'download_link'
        index_together = [('url', 'ip_address', 'created_by')]
