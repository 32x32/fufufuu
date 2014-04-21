from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.dmca.models import DmcaAccount


class DmcaListViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user.dmca_account = DmcaAccount.objects.create(
            name='Corporation Name',
            email='example@corporation.com',
            website='http://corporation.com'
        )
        self.user.save()

    def test_dmca_list_view_get_no_account(self):
        self.user.dmca_account.delete()

        response = self.client.get(reverse('dmca.list'))
        self.assertEqual(response.status_code, 404)

    def test_dmca_list_view_get(self):
        response = self.client.get(reverse('dmca.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dmca/dmca-list.html')
