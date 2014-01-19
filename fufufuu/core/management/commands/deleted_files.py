import os
import traceback
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from fufufuu.core.models import DeletedFile


class Command(BaseCommand):

    def clear(self):
        errors = []
        for deleted_file in DeletedFile.objects.filter(delete_after__lte=timezone.now()):
            if os.path.exists(deleted_file.path):
                try:
                    os.remove(deleted_file.path)
                except Exception:
                    errors.append(traceback.format_exc())
                    continue
            deleted_file.delete()

        # TODO: email errors to admin

    def info(self):
        print('{} files scheduled for deletion'.format(DeletedFile.objects.all().count()))
        print('{} files can be deleted immediately'.format(DeletedFile.objects.filter(delete_after__lte=timezone.now()).count()))

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify an operation for deleted_files.')

        command = args[0]
        if not hasattr(self, command):
            raise CommandError('The specified operation does not exist.')

        getattr(self, command)()
