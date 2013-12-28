from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.models import Manga


class UploadListViewTests(BaseTestCase):

    def test_upload_list_view_get(self):
        response = self.client.get(reverse('upload.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload/upload-list.html')

    def test_upload_list_view_post_limit(self):
        for i in range(self.user.upload_limit+1):
            Manga().save(updated_by=self.user)

        response = self.client.post(reverse('upload.list'))
        self.assertRedirects(response, reverse('upload.list'))

    def test_upload_list_view_post(self):
        response = self.client.post(reverse('upload.list'))
        manga = Manga.objects.latest('created_on')
        self.assertRedirects(response, reverse('manga.edit.images', args=[manga.id, manga.slug]))
