from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class MangaListViewTests(BaseTestCase):

    def test_manga_list_view_get(self):
        response = self.client.get(reverse('manga.list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, 'manga/manga-list.html')
