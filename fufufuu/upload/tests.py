from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class UploadListViewTests(BaseTestCase):

    def test_upload_list_view_get(self):
        response = self.client.get(reverse('upload.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload/upload-list.html')
