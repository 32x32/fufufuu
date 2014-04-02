from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase


class ModeratorReportMangaListViewTests(BaseTestCase):

    def test_moderator_report_manga_list_view_get(self):
        response = self.client.get(reverse('moderator.report.manga.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'moderator/moderator-report-manga-list.html')
