import os
import zipfile
from io import BytesIO

from django.contrib.contenttypes.models import ContentType
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse

from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.core.utils import slugify
from fufufuu.download.models import DownloadLink
from fufufuu.manga.enums import MangaStatus, MangaCategory
from fufufuu.manga.models import Manga, MangaFavorite, MangaArchive
from fufufuu.manga.utils import generate_manga_archive
from fufufuu.revision.enums import RevisionStatus
from fufufuu.revision.models import Revision
from fufufuu.tag.models import Tag


class MangaListViewTests(BaseTestCase):

    def test_manga_list_view_get(self):
        response = self.client.get(reverse('manga.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-list.html')

    def test_manga_list_view_post(self):
        response = self.client.post(reverse('manga.list'), {
            'non_h': 'on',
            'lang': Language.ENGLISH,
        })
        self.assertRedirects(response, reverse('manga.list'))

        filters = self.client.session['manga_list_filters']
        self.assertTrue(filters.get('non_h'))
        self.assertFalse(filters.get('ecchi'))
        self.assertEqual(filters.get('lang'), Language.ENGLISH)

class MangaListFavoritesViewTests(BaseTestCase):

    def test_manga_list_favorites_view_get(self):
        response = self.client.get(reverse('manga.list.favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-list.html')

    def test_manga_list_favorites_view_get_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse('manga.list.favorites'))
        self.assertRedirects(response, '{}?next={}'.format(
            reverse('account.login'),
            reverse('manga.list.favorites')
        ))


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


class MangaInfoViewTests(BaseTestCase):

    def test_manga_info_view_get(self):
        response = self.client.get(reverse('manga.info', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-info.html')

    def test_manga_info_view_get_no_archive_file(self):
        archive = generate_manga_archive(self.manga)
        os.remove(archive.file.path)

        response = self.client.get(reverse('manga.info', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-info.html')

        archive = MangaArchive.objects.get(manga=self.manga)
        self.assertTrue(os.path.exists(archive.file.path))


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


class MangaDownloadViewTests(BaseTestCase):

    def test_manga_download_view_get(self):
        response = self.client.get(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 405)

    def test_manga_download_view_post(self):
        response = self.client.post(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 302)
        download_link = DownloadLink.objects.latest('created_on')
        self.assertEqual(response['location'], 'http://testserver{}'.format(reverse('download', args=[download_link.key, self.manga.archive_name])))

    def test_manga_download_view_post_draft(self):
        self.manga.status = MangaStatus.DRAFT
        self.manga.save(updated_by=self.user)

        response = self.client.post(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)


class MangaReportViewTests(BaseTestCase):

    def test_manga_report_view_get(self):
        response = self.client.get(reverse('manga.report', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-report.html')


class MangaRevisionsViewTests(BaseTestCase):

    def test_manga_revisions_view_get(self):
        response = self.client.get(reverse('manga.revisions', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-revisions.html')


class MangaFavoriteViewTests(BaseTestCase):

    def test_manga_favorite_view_get(self):
        response = self.client.get(reverse('manga.favorite', args=[self.manga.id, self.manga.slug]))
        self.assertRedirects(response, reverse('manga.info', args=[self.manga.id, self.manga.slug]))

    def test_manga_favorite_view_post(self):
        self.assertFalse(MangaFavorite.objects.filter(manga=self.manga, user=self.user).exists())

        response = self.client.post(reverse('manga.favorite', args=[self.manga.id, self.manga.slug]))
        self.assertRedirects(response, reverse('manga.info', args=[self.manga.id, self.manga.slug]))
        self.assertTrue(MangaFavorite.objects.filter(manga=self.manga, user=self.user).exists())

        response = self.client.post(reverse('manga.favorite', args=[self.manga.id, self.manga.slug]), {
            'next': reverse('manga', args=[self.manga.id, self.manga.slug]),
        })
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]))
        self.assertFalse(MangaFavorite.objects.filter(manga=self.manga, user=self.user).exists())


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

    def test_manga_edit_view_get_with_revision(self):
        self.manga.status = MangaStatus.PUBLISHED
        self.manga.save(self.user)

        user = self.create_test_user('testuser2')
        self.client.login(username='testuser2', password='password')

        self.manga.title = 'Revision Title'
        self.manga.create_revision(user, Tag.objects.all()[:1])

        response = self.client.get(reverse('manga.edit', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit.html')

    def test_manga_edit_view_post_with_revision(self):
        self.manga.status = MangaStatus.PUBLISHED
        self.manga.save(self.user)

        user = self.create_test_user('testuser2')
        self.client.login(username='testuser2', password='password')

        self.manga.title = 'Revision Title'
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {
            'title': 'Revision Title 2',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'save',
        })
        self.assertRedirects(response, reverse('manga.edit', args=[self.manga.id, self.manga.slug]))

        ct = ContentType.objects.get_for_model(self.manga)
        new_revision = Revision.objects.get(
            content_type__id=ct.id,
            object_id=self.manga.id,
            status=RevisionStatus.PENDING,
            created_by=user
        )
        self.assertEqual(new_revision.diff['title'], ('Test Manga 1', 'Revision Title 2'))


class MangaEditImagesViewTests(BaseTestCase):

    def test_manga_edit_images_view_get(self):
        response = self.client.get(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit-images.html')

    def test_manga_edit_images_view_get_moderator(self):
        user = self.create_test_user('testuser2')
        self.manga.created_by = user
        self.manga.save(user)

        response = self.client.get(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit-images.html')

    def test_manga_edit_images_view_get_not_allowed(self):
        user = self.create_test_user('testuser2')
        self.manga.created_by = user
        self.manga.save(user)

        self.user.is_moderator = False
        self.user.save()

        response = self.client.get(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)

        self.client.login(username='testuser2', password='password')

        response = self.client.get(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit-images.html')

    def test_manga_edit_images_view_post_invalid(self):
        manga_page = self.manga.mangapage_set.all()[0]
        response = self.client.post(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]), {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '100',
            'form-0-id': manga_page.id,
            'action': 'set_cover',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit-images.html')

    def test_manga_edit_images_view_post(self):
        manga_page = self.manga.mangapage_set.all()[0]
        response = self.client.post(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]), {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MAX_FORMS': '1',
            'form-0-id': manga_page.id,
            'action': 'reorder'
        })
        self.assertRedirects(response, reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))


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


class MangaEditImagesPageView(BaseTestCase):

    def test_edit_images_page_view_get(self):
        manga_page = self.manga.mangapage_set.all()[0]
        manga_page.image = SimpleUploadedFile('01.jpg', self.create_test_image_file().getvalue())
        manga_page.save()

        response = self.client.get(reverse('manga.edit.images.page', args=[self.manga.id, self.manga.slug, manga_page.page]))
        self.assertEqual(response['location'], 'http://testserver{}'.format(manga_page.image.url))

    def test_edit_images_page_view_get_no_allowed(self):
        manga_page = self.manga.mangapage_set.all()[0]
        manga_page.image = SimpleUploadedFile('01.jpg', self.create_test_image_file().getvalue())
        manga_page.save()

        user = self.create_test_user('testuser2')
        self.manga.created_by = user
        self.manga.save(user)

        self.user.is_moderator = False
        self.user.save()

        response = self.client.get(reverse('manga.edit.images.page', args=[self.manga.id, self.manga.slug, manga_page.page]))
        self.assertEqual(response.status_code, 404)
