import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from fufufuu.core.tests import BaseTestCase
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image


class ImageModelTests(BaseTestCase):

    def tests_image_replace_file(self):
        self.manga.cover = SimpleUploadedFile('test.jpg', self.create_test_image_file().getvalue())
        self.manga.save(self.user)

        image = Image(key_type=ImageKeyType.MANGA_THUMB, key_id=1)
        image.save(self.manga.cover.path)

        path = image.file.path
        self.assertTrue(os.path.exists(path))

        image.save(self.manga.cover.path)
        self.assertNotEqual(path, image.file.path)
        self.assertFalse(os.path.exists(path))

    def test_image_delete(self):
        self.manga.cover = SimpleUploadedFile('test.jpg', self.create_test_image_file().getvalue())
        self.manga.save(self.user)

        image = Image(key_type=ImageKeyType.MANGA_THUMB, key_id=1)
        image.save(self.manga.cover.path)

        path = image.file.path
        self.assertTrue(os.path.exists(path))

        Image.safe_delete(key_type=ImageKeyType.MANGA_THUMB, key_id=1)
        self.assertFalse(os.path.exists(path))


class ImageViewTests(BaseTestCase):

    def test_image_view_get_invalid_key_type(self):
        response = self.client.get(reverse('image', args=['invalid_key_type', 'invalid_id']))
        self.assertEqual(response.status_code, 404)

    def test_image_view_get_invalid_key_id(self):
        response = self.client.get(reverse('image', args=[ImageKeyType.MANGA_COVER, 'invalid_id']))
        self.assertEqual(response.status_code, 404)

    def test_image_view_get_not_found(self):
        response = self.client.get(reverse('image', args=[ImageKeyType.MANGA_COVER, '192873']))
        self.assertEqual(response.status_code, 404)

    # def test_image_view_get_missing_file(self):
    #     image_file = self.create_test_image_file()
    #     image_file = SimpleUploadedFile('test.jpg', image_file.getvalue())
    #     manga_page = MangaPage.objects.create(manga=self.manga, page=1, image=image_file)
    #
    #     image_resize(manga_page.image, ImageKeyType.MANGA_COVER, self.manga.id)
    #     image_obj = Image.objects.get(key_type=ImageKeyType.MANGA_COVER, key_id=self.manga.id)
    #     original_path = image_obj.file.path
    #     os.remove(image_obj.file.path)
    #
    #     response = self.client.get(reverse('image', args=[image_obj.key_type, int_to_base36(image_obj.key_id)]))
    #
    #     image_obj = Image.objects.get(key_type=ImageKeyType.MANGA_COVER, key_id=self.manga.id)
    #     self.assertNotEqual(original_path, image_obj.file.path)
    #     self.assertEqual(response['location'], 'http://testserver{}'.format(image_obj.file.url))
