from django.db import models

from fufufuu.manga.models import Manga


class DmcaAccount(models.Model):

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    website = models.CharField(max_length=2048, blank=True, null=True)
    markdown = models.TextField(blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dmca_account'


class DmcaRequest(models.Model):

    dmca_account = models.ForeignKey(DmcaAccount)
    manga = models.ForeignKey(Manga)
    comment = models.TextField(blank=True, null=True)

    created_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dmca_request'
