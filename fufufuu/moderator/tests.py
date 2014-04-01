from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class ModeratorDashboardViewTests(BaseTestCase):

    def test_moderator_dashboard_view_get(self):
        response = self.client.get(reverse('moderator.dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/moderator-dashboard.html')
