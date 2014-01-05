import os
from django.core.files.base import File
from fufufuu.core.tests import BaseTestCase
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image


class ImageModelTests(BaseTestCase):

    def test_image_replace_file(self):
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
