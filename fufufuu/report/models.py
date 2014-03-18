from django.db import models
from fufufuu.account.models import User
from fufufuu.manga.models import Manga


class ReportManga(models.Model):

    manga = models.ForeignKey(Manga)

    report_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    comment = models.TextField()

    created_by = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_manga'
        index_together = [('manga', 'status')]
