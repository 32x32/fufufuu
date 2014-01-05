import os
import shutil
import sys
from django.core.management.base import BaseCommand, CommandError
from fufufuu.image.models import Image
from fufufuu.settings import MEDIA_ROOT


class Command(BaseCommand):

    def clear(self):
        count = Image.objects.all().count()
        Image.objects.all().delete()
        shutil.rmtree(os.path.join(MEDIA_ROOT, 'image'), ignore_errors=True)
        sys.stdout.write('Removed {} images from cache.\n'.format(count))

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify an operation for image_cache.')

        command = args[0]
        if not hasattr(self, command):
            raise CommandError('The specified operation does not exist.')

        getattr(self, command)()
