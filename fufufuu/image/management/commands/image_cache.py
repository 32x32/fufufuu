import os
import shutil
from django.core.management.base import BaseCommand, CommandError
from django.db.models.aggregates import Count
from fufufuu.image.models import Image
from fufufuu.settings import MEDIA_ROOT


class Command(BaseCommand):

    def info(self):
        for d in Image.objects.values('key_type').annotate(count=Count('key_type')):
            print('{} - {}'.format(d['key_type'].lower(), d['count']))

    def clear(self):
        count = Image.objects.all().count()
        Image.objects.all().delete()
        shutil.rmtree(os.path.join(MEDIA_ROOT, 'image'), ignore_errors=True)
        print('Removed {} images from cache.\n'.format(count))

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify an operation for image_cache.')

        command = args[0]
        if not hasattr(self, command):
            raise CommandError('The specified operation does not exist.')

        getattr(self, command)()
