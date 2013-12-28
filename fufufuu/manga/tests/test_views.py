from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.enums import MangaStatus


class MangaListViewTests(BaseTestCase):

    def test_manga_list_view_get(self):
        response = self.client.get(reverse('manga.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-list.html')


class MangaViewTests(BaseTestCase):

    def test_manga_view_get(self):
        response = self.client.get(reverse('manga', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga.html')

    def test_manga_view_get_draft(self):
        self.manga.status = MangaStatus.DRAFT
        self.manga.save(updated_by=self.user)
        response = self.client.get(reverse('manga', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)


class MangaThumbnailsViewTests(BaseTestCase):

    def test_manga_thumbnails_view_get(self):
        response = self.client.get(reverse('manga.thumbnails', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-thumbnails.html')


class MangaCommentsViewTests(BaseTestCase):

    def test_manga_comments_view_get(self):
        response = self.client.get(reverse('manga.comments', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-comments.html')


class MangaDownloadView(BaseTestCase):

    def test_manga_thumbnail_view_get(self):
        response = self.client.get(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-download.html')


class MangaReportViewTests(BaseTestCase):

    def test_manga_thumbnail_view_get(self):
        response = self.client.get(reverse('manga.report', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-report.html')


class MangaHistoryViewTests(BaseTestCase):

    def test_manga_history_view_get(self):
        response = self.client.get(reverse('manga.history', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-history.html')


class MangaEditViewTests(BaseTestCase):

    def test_manga_edit_view_get(self):
        pass

    def test_manga_edit_view_post_invalid(self):
        pass

    def test_manga_edit_view_post(self):
        pass


class MangaEditImagesViewTests(BaseTestCase):

    def test_manga_edit_images_view_get(self):
        pass

    def test_manga_edit_images_view_post_invalid(self):
        pass

    def test_manga_edit_images_view_post(self):
        pass
