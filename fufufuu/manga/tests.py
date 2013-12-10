from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class MangaListViewTests(BaseTestCase):

    def test_manga_list_view_get(self):
        response = self.client.get(reverse('manga.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-list.html')


class MangaModelTests(BaseTestCase):

    def test_manga_save_slugify(self):
        pass

    def test_manga_delete_draft(self):
        pass

    def test_manga_delete_force_delete(self):
        pass

    def test_manga_delete(self):
        pass

    def test_manga_image_delete(self):
        pass

    def test_manga_archive_delete(self):
        pass
