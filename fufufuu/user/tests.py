from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class UserViewTests(BaseTestCase):

    def test_user_view_get(self):
        response = self.client.get(reverse('user', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/user.html')

    def test_user_view_get_404(self):
        response = self.client.get(reverse('user', args=['non_existent']))
        self.assertEqual(response.status_code, 404)


class UserUploadsViewTests(BaseTestCase):

    def test_user_uploads_view(self):
        response = self.client.get(reverse('user.uploads', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/user-uploads.html')
