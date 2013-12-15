from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.enums import MangaStatus
from fufufuu.manga.models import Manga


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


class MangaModelTests(BaseTestCase):

    def test_manga_save_slugify(self):
        pass

    def test_manga_delete_draft(self):
        pass

    def test_manga_delete_force_delete(self):
        pass

    def test_manga_delete(self):
        pass

    def test_manga_image_delete(self):
        pass

    def test_manga_archive_delete(self):
        pass

    def assert_manga_exists(self, manager, status, exists):
        self.manga.status = status
        self.manga.save(updated_by=self.user)
        self.assertEqual(manager.filter(id=self.manga.id).exists(), exists)

    def test_manga_objects_manager(self):
        self.assert_manga_exists(Manga.objects, MangaStatus.DRAFT, True)
        self.assert_manga_exists(Manga.objects, MangaStatus.PUBLISHED, True)
        self.assert_manga_exists(Manga.objects, MangaStatus.PENDING, True)
        self.assert_manga_exists(Manga.objects, MangaStatus.DELETED, False)

    def test_manga_published_manager(self):
        self.assert_manga_exists(Manga.published, MangaStatus.DRAFT, False)
        self.assert_manga_exists(Manga.published, MangaStatus.PUBLISHED, True)
        self.assert_manga_exists(Manga.published, MangaStatus.PENDING, False)
        self.assert_manga_exists(Manga.published, MangaStatus.DELETED, False)

    def test_manga_all_manager(self):
        self.assert_manga_exists(Manga.all, MangaStatus.DRAFT, True)
        self.assert_manga_exists(Manga.all, MangaStatus.PUBLISHED, True)
        self.assert_manga_exists(Manga.all, MangaStatus.PENDING, True)
        self.assert_manga_exists(Manga.all, MangaStatus.DELETED, True)
