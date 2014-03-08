from django.core.urlresolvers import reverse
from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase


class SearchViewTests(BaseTestCase):

    def test_search_view_get(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')

    def test_search_view_post(self):
        response = self.client.post(reverse('search'), {
            'non_h': 'on',
            'lang': Language.ENGLISH,
            'q': 'Test Manga',
        })
        self.assertRedirects(response, '{}?q={}'.format(reverse('search'), 'Test%20Manga'))
