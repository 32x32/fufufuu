from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class StaffViewTests(BaseTestCase):

    def test_staff_view_get_non_staff(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse('staff'))
        self.assertEqual(response.status_code, 404)

    def test_staff_view_get(self):
        response = self.client.get(reverse('staff'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff.html')
