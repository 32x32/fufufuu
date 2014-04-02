from django.db import models

from fufufuu.account.models import User
from fufufuu.manga.models import Manga
from fufufuu.report.enums import ReportMangaType, ReportStatus


class ReportMangaResolution(models.Model):

    removed         = models.BooleanField()
    comment         = models.TextField(blank=True, null=True)

    created_by      = models.ForeignKey(User)
    created_on      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'report_manga_resolution'


class ReportMangaOpenManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=ReportStatus.OPEN)


class ReportMangaClosedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(status=ReportStatus.CLOSED)


class ReportManga(models.Model):

    manga           = models.ForeignKey(Manga)

    status          = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.OPEN)
    type            = models.CharField(max_length=20, choices=ReportMangaType.choices)
    resolution      = models.ForeignKey(ReportMangaResolution, blank=True, null=True)
    comment         = models.TextField(blank=True, null=True)
    ip_address      = models.CharField(max_length=200, blank=True, null=True)
    weight          = models.DecimalField(max_digits=19, decimal_places=10)

    created_by      = models.ForeignKey(User, blank=True, null=True)
    created_on      = models.DateTimeField(auto_now_add=True)

    open            = ReportMangaOpenManager()
    closed          = ReportMangaClosedManager()
    all             = models.Manager()

    class Meta:
        db_table = 'report_manga'
        index_together = [('status', 'manga')]
