import zipfile
from io import BytesIO
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.core.utils import slugify
from fufufuu.manga.enums import MangaStatus, MangaCategory
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

    def setUp(self):
        super().setUp()
        self.manga.status = MangaStatus.DRAFT
        self.manga.save(updated_by=self.user)

    def test_manga_edit_view_get(self):
        response = self.client.get(reverse('manga.edit', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit.html')

    def test_manga_edit_view_post_invalid(self):
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {
            'action': 'unknown action',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit.html')

    def test_manga_edit_view_post_save(self):
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'save',
        })
        self.assertRedirects(response, reverse('manga.edit', args=[self.manga.id, slugify('Test Manga Title')]))

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.title, 'Test Manga Title')
        self.assertEqual(manga.category, MangaCategory.VANILLA)
        self.assertEqual(manga.language, Language.ENGLISH)
        self.assertEqual(manga.status, MangaStatus.DRAFT)

    def test_manga_edit_view_post_publish(self):
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'publish',
        })
        self.assertRedirects(response, reverse('manga.edit', args=[self.manga.id, slugify('Test Manga Title')]))

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.title, 'Test Manga Title')
        self.assertEqual(manga.category, MangaCategory.VANILLA)
        self.assertEqual(manga.language, Language.ENGLISH)
        self.assertEqual(manga.status, MangaStatus.PUBLISHED)

    def test_manga_edit_view_post_delete_published(self):
        self.manga.status = MangaStatus.PUBLISHED
        self.manga.save(updated_by=self.user)

        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {'action': 'delete'})
        self.assertRedirects(response, reverse('upload.list'))

        manga = Manga.all.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.DELETED)

    def test_manga_edit_view_post_delete_draft(self):
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {'action': 'delete'})
        self.assertRedirects(response, reverse('upload.list'))
        self.assertFalse(Manga.objects.filter(id=self.manga.id).exists())


class MangaEditImagesViewTests(BaseTestCase):

    def test_manga_edit_images_view_get(self):
        pass

    def test_manga_edit_images_view_post_invalid(self):
        pass

    def test_manga_edit_images_view_post(self):
        pass


class MangaEditUploadViewTests(BaseTestCase):

    def test_manga_edit_upload_view_get(self):
        response = self.client.get(reverse('manga.edit.upload', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 405)

    def test_manga_edit_upload_view_post_empty(self):
        response = self.client.post(reverse('manga.edit.upload', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)

    def test_manga_edit_upload_view_post_zipfile(self):
        content = self.create_test_image_file().getvalue()

        upload_file = BytesIO()
        upload_file_zip = zipfile.ZipFile(upload_file, 'w')
        upload_file_zip.writestr('01.png', bytes(content))
        upload_file_zip.writestr('02.png', bytes(content))
        upload_file_zip.writestr('03.png', bytes('0', 'utf-8'))
        upload_file_zip.close()

        response = self.client.post(reverse('manga.edit.upload', args=[self.manga.id, self.manga.slug]), {
            'zipfile': SimpleUploadedFile('test.zip', upload_file.getvalue()),
        })
        self.assertRedirects(response, reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))

    def test_manga_edit_upload_view_post_images(self):
        content = self.create_test_image_file().getvalue()
        response = self.client.post(reverse('manga.edit.upload', args=[self.manga.id, self.manga.slug]), {
            'images': [
                SimpleUploadedFile('01.png', File(content)),
                SimpleUploadedFile('02.png', File(content)),
                SimpleUploadedFile('03.png', File(content)),
            ]
        })
        self.assertRedirects(response, reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
