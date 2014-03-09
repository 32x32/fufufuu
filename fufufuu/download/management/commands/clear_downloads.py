import datetime

import pytz
from django.core.management.base import BaseCommand

from fufufuu.download.models import DownloadLink


class Command(BaseCommand):
    """
    Delete all download links that are more than an hour old.
    """

    def handle(self, *args, **options):
        cutoff = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(hours=1)
        return DownloadLink.objects.filter(created_on__lt=cutoff).delete()
