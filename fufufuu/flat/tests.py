from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class FlatMarkdownViewTests(BaseTestCase):

    def test_flat_markdown_view_get(self):
        response = self.client.get(reverse('flat.markdown'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flat/flat-markdown.html')
