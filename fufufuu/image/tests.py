import os
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from fufufuu.core.tests import BaseTestCase, suppress_output
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image
from fufufuu.image.models import Image
from fufufuu.manga.models import MangaPage


class ImageModelTests(BaseTestCase):

    def tests_image_replace_file(self):
        image = Image(key_type=ImageKeyType.MANGA_THUMB, key_id=1)
        image.save(File(self.create_test_image_file()))

        path = image.file.path
        self.assertTrue(os.path.exists(path))

        image.save(File(self.create_test_image_file()))
        self.assertNotEqual(path, image.file.path)
        self.assertFalse(os.path.exists(path))

    def test_image_delete(self):
        image = Image(key_type=ImageKeyType.MANGA_THUMB, key_id=1)
        image.save(File(self.create_test_image_file()))

        path = image.file.path
        self.assertTrue(os.path.exists(path))

        image.delete()
        self.assertFalse(os.path.exists(path))


class ImageManagementTests(BaseTestCase):

    @suppress_output
    def test_image_cache_info(self):
        call_command('image_cache', 'info')

    @suppress_output
    def test_image_cache_clear(self):
        image_file = self.create_test_image_file()
        image_file = SimpleUploadedFile('test.jpg', image_file.getvalue())
        manga_page = MangaPage.objects.create(manga=self.manga, page=1, image=image_file)

        image(manga_page.image, ImageKeyType.MANGA_COVER, self.manga.id)
        self.assertTrue(Image.objects.all().count())

        call_command('image_cache', 'clear')
        self.assertFalse(Image.objects.all().count())
