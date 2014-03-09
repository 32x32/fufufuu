import datetime
import pytz

from django.core.management import call_command
from django.core.urlresolvers import reverse

from fufufuu.core.tests import BaseTestCase
from fufufuu.download.models import DownloadLink
from fufufuu.manga.utils import generate_manga_archive


class DownloadViewTests(BaseTestCase):

    def test_download_view_get(self):
        manga_archive = generate_manga_archive(self.manga)

        download_link = DownloadLink.objects.create(
            url=manga_archive.file.url,
            ip_address='127.0.0.1',
            created_by=self.user,
        )

        response = self.client.get(reverse('download', args=[download_link.key, manga_archive.name]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver{}'.format(manga_archive.file.url))


class DownloadManagementTests(BaseTestCase):

    def test_clear_downloads(self):
        now = datetime.datetime.now(tz=pytz.UTC)

        manga_archive = generate_manga_archive(self.manga)
        download_link1 = DownloadLink.objects.create(
            url=manga_archive.file.url,
            ip_address='some-ip-address',
            created_by=self.user,
        )
        download_link1.created_on = now - datetime.timedelta(minutes=90)
        download_link1.save()

        download_link2 = DownloadLink.objects.create(
            url=manga_archive.file.url,
            ip_address='some-ip-address',
            created_by=self.user,
        )
        download_link2.created_on = now - datetime.timedelta(minutes=30)
        download_link2.save()

        call_command('clear_downloads')

        self.assertFalse(DownloadLink.objects.filter(id=download_link1.id).exists())
        self.assertTrue(DownloadLink.objects.filter(id=download_link2.id).exists())
