import logging
import os
import traceback

from django.core.management.base import BaseCommand
from django.utils import timezone

from fufufuu.core.models import DeletedFile


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Deletes core.DeletedFile files from the file system.
    """

    def handle(self, *args, **options):
        error_list = []
        for deleted_file in DeletedFile.objects.filter(delete_after__lte=timezone.now()):
            if os.path.exists(deleted_file.path):
                try:
                    os.remove(deleted_file.path)
                except Exception:
                    error_list.append(traceback.format_exc())
                    continue
            deleted_file.delete()

        for error in error_list:
            logging.error(error)
