import zipfile
from io import BytesIO
from django.contrib.auth.models import AnonymousUser

from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.http.response import Http404
from fufufuu.core.enums import SiteSettingKey

from fufufuu.core.languages import Language
from fufufuu.core.models import SiteSetting
from fufufuu.core.tests import BaseTestCase
from fufufuu.core.utils import slugify
from fufufuu.dmca.models import DmcaAccount
from fufufuu.download.models import DownloadLink
from fufufuu.manga.enums import MangaStatus, MangaCategory
from fufufuu.manga.exceptions import MangaDmcaException
from fufufuu.manga.models import Manga, MangaFavorite
from fufufuu.manga.views import BaseMangaView
from fufufuu.report.enums import ReportMangaType
from fufufuu.report.models import ReportManga
from fufufuu.tag.enums import TagType
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
        self.assertTemplateUsed(response, 'manga/manga-list-favorites.html')

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
        self.user.is_staff = False
        self.user.is_moderator = False
        self.user.save()

        self.manga.status = MangaStatus.DRAFT
        self.manga.save(updated_by=self.user)
        response = self.client.get(reverse('manga', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)

    def test_manga_view_get_no_slug(self):
        response = self.client.get(reverse('manga', args=[self.manga.id]))
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]), status_code=301)


class MangaThumbnailsViewTests(BaseTestCase):

    def test_manga_thumbnails_view_get(self):
        response = self.client.get(reverse('manga.thumbnails', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-thumbnails.html')


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
        self.user.is_staff = False
        self.user.is_moderator = False
        self.user.save()

        self.manga.status = MangaStatus.DRAFT
        self.manga.save(updated_by=self.user)

        response = self.client.post(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)

    def test_manga_download_view_post_disabled(self):
        SiteSetting.set_val(SiteSettingKey.ENABLE_DOWNLOADS, False, self.user)
        response = self.client.post(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)


class MangaReportViewTests(BaseTestCase):

    def test_manga_report_view_get(self):
        response = self.client.get(reverse('manga.report', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-report.html')

    def test_manga_report_view_post_invalid(self):
        response = self.client.post(reverse('manga.report', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-report.html')

    def test_manga_report_view_post_anonymous_invalid(self):
        self.client.logout()
        response = self.client.post(reverse('manga.report', args=[self.manga.id, self.manga.slug]), {
            'type': ReportMangaType.COPYRIGHT,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-report.html')

    def test_manga_report_view_post_anonymous(self):
        from captcha.conf import settings
        from captcha.models import CaptchaStore

        challenge, response = settings.get_challenge()()
        store = CaptchaStore.objects.create(challenge=challenge, response=response)

        self.client.logout()
        response = self.client.post(reverse('manga.report', args=[self.manga.id, self.manga.slug]), {
            'type': ReportMangaType.COPYRIGHT,
            'check': 'on',
            'captcha_0': store.hashkey,
            'captcha_1': store.response,
        })
        self.assertRedirects(response, reverse('manga.list'))

    def test_manga_report_view_post(self):
        ReportManga.open.filter(manga=self.manga, created_by=self.user).delete()
        response = self.client.post(reverse('manga.report', args=[self.manga.id, self.manga.slug]), {
            'type': ReportMangaType.COPYRIGHT,
            'comment': 'This is a standard copyright violation.',
            'check': 'on',
        })
        self.assertRedirects(response, reverse('manga.list'))


class MangaFavoriteViewTests(BaseTestCase):

    def test_manga_favorite_view_get(self):
        response = self.client.get(reverse('manga.favorite', args=[self.manga.id, self.manga.slug]))
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]))

    def test_manga_favorite_view_post(self):
        self.assertFalse(MangaFavorite.objects.filter(manga=self.manga, user=self.user).exists())

        response = self.client.post(reverse('manga.favorite', args=[self.manga.id, self.manga.slug]))
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]))
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

    def test_manga_edit_view_get_tank(self):
        tank = Tag.objects.filter(tag_type=TagType.TANK)[0]
        self.manga.tank = tank
        self.manga.tank_chapter = '1'
        self.manga.save(self.user)

        response = self.client.get(reverse('manga.edit', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-edit.html')
        self.assertTrue(tank.name in str(response.content))

    def test_manga_edit_view_post_remove(self):
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'remove',
        })
        self.assertRedirects(response, reverse('manga.list'))

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.REMOVED)

    def test_manga_edit_view_post_remove_not_moderator(self):
        self.user.is_moderator = False
        self.user.save()

        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]), {
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'remove',
        })
        self.assertRedirects(response, reverse('manga.edit', args=[self.manga.id, slugify('Test Manga Title')]))

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.DRAFT)


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

        self.user.is_staff = False
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

        self.user.is_staff = False
        self.user.is_moderator = False
        self.user.save()

        response = self.client.get(reverse('manga.edit.images.page', args=[self.manga.id, self.manga.slug, manga_page.page]))
        self.assertEqual(response.status_code, 404)


class MangaViewMixinTests(BaseTestCase):

    def _assert_get_manga(self, method_name, user, manga_status, error_cls):
        class TestRequest: pass

        mixin = BaseMangaView()
        mixin.request = TestRequest()
        mixin.request.user = user

        self.manga.status = manga_status
        self.manga.save(self.user)

        if error_cls:
            try:
                getattr(mixin, method_name)(self.manga.id)
                self.fail('Exception not raised, expected {}'.format(error_cls))
            except error_cls:
                pass
        else:
            self.assertEqual(self.manga, getattr(mixin, method_name)(self.manga.id))

    def assert_get_manga_for_view(self, user, manga_status, error_cls=None):
        self._assert_get_manga('get_manga_for_view', user, manga_status, error_cls)

    def assert_get_manga_for_edit(self, user, manga_status, error_cls=None):
        self._assert_get_manga('get_manga_for_edit', user, manga_status, error_cls)

    def test_get_manga_for_view_unauthenticated(self):
        user = AnonymousUser()
        self.assert_get_manga_for_view(user, MangaStatus.DRAFT, Http404)
        self.assert_get_manga_for_view(user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_view(user, MangaStatus.PENDING, Http404)
        self.assert_get_manga_for_view(user, MangaStatus.REMOVED, Http404)
        self.assert_get_manga_for_view(user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_view(user, MangaStatus.DMCA, MangaDmcaException)

    def test_get_manga_for_view_staff(self):
        self.user.is_staff = True
        self.user.is_moderator = False
        self.user.save()

        self.assert_get_manga_for_view(self.user, MangaStatus.DRAFT)
        self.assert_get_manga_for_view(self.user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_view(self.user, MangaStatus.PENDING)
        self.assert_get_manga_for_view(self.user, MangaStatus.REMOVED)
        self.assert_get_manga_for_view(self.user, MangaStatus.DELETED)
        self.assert_get_manga_for_view(self.user, MangaStatus.DMCA)

    def test_get_manga_for_view_moderator(self):
        self.user.is_staff = False
        self.user.is_moderator = True
        self.user.save()

        self.assert_get_manga_for_view(self.user, MangaStatus.DRAFT)
        self.assert_get_manga_for_view(self.user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_view(self.user, MangaStatus.PENDING)
        self.assert_get_manga_for_view(self.user, MangaStatus.REMOVED)
        self.assert_get_manga_for_view(self.user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_view(self.user, MangaStatus.DMCA, MangaDmcaException)

    def test_get_manga_for_view(self):
        self.user.is_staff = False
        self.user.is_moderator = False
        self.user.save()

        self.assert_get_manga_for_view(self.user, MangaStatus.DRAFT, Http404)
        self.assert_get_manga_for_view(self.user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_view(self.user, MangaStatus.PENDING, Http404)
        self.assert_get_manga_for_view(self.user, MangaStatus.REMOVED, Http404)
        self.assert_get_manga_for_view(self.user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_view(self.user, MangaStatus.DMCA, MangaDmcaException)

    def test_get_manga_for_edit_unauthenticated(self):
        user = AnonymousUser()
        self.assert_get_manga_for_edit(user, MangaStatus.DRAFT, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.PUBLISHED, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.PENDING, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.REMOVED, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.DMCA, Http404)

    def test_get_manga_for_edit_staff(self):
        self.user.is_staff = True
        self.user.is_moderator = False
        self.user.save()

        self.assert_get_manga_for_edit(self.user, MangaStatus.DRAFT)
        self.assert_get_manga_for_edit(self.user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.PENDING)
        self.assert_get_manga_for_edit(self.user, MangaStatus.REMOVED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.DELETED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.DMCA)

    def test_get_manga_for_edit_moderator(self):
        self.user.is_staff = False
        self.user.is_moderator = True
        self.user.save()

        self.assert_get_manga_for_edit(self.user, MangaStatus.DRAFT)
        self.assert_get_manga_for_edit(self.user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.PENDING)
        self.assert_get_manga_for_edit(self.user, MangaStatus.REMOVED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_edit(self.user, MangaStatus.DMCA, MangaDmcaException)

    def test_get_manga_for_edit_owner(self):
        self.user.is_staff = False
        self.user.is_moderator = False
        self.user.save()

        self.assert_get_manga_for_edit(self.user, MangaStatus.DRAFT)
        self.assert_get_manga_for_edit(self.user, MangaStatus.PUBLISHED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.PENDING)
        self.assert_get_manga_for_edit(self.user, MangaStatus.REMOVED)
        self.assert_get_manga_for_edit(self.user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_edit(self.user, MangaStatus.DMCA, MangaDmcaException)

    def test_get_manga_for_edit_not_owner(self):
        user = self.create_test_user('testuser2')
        user.is_staff = False
        user.is_moderator = False
        user.save()

        self.assert_get_manga_for_edit(user, MangaStatus.DRAFT, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.PUBLISHED, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.PENDING,  Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.REMOVED, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.DELETED, Http404)
        self.assert_get_manga_for_edit(user, MangaStatus.DMCA, Http404)


class MangaDmcaRequestViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user.dmca_account = DmcaAccount.objects.create(
            name='Corporation Name',
            email='example@corporation.com',
            website='http://corporation.com'
        )
        self.user.save()

    def test_manga_dmca_request_view_get_non_dmca_account(self):
        self.user.dmca_account.delete()
        response = self.client.get(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)

    def test_manga_dmca_request_view_get_already_dmca(self):
        self.manga.status = MangaStatus.DMCA
        self.manga.save(updated_by=self.user)

        response = self.client.get(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]))
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]))

    def test_manga_dmca_request_view_get(self):
        response = self.client.get(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca-request.html')

    def test_manga_dmca_request_view_post_non_dmca_account(self):
        self.user.dmca_account.delete()
        response = self.client.post(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 404)

    def test_manga_dmca_request_view_post_already_dmca(self):
        self.manga.status = MangaStatus.DMCA
        self.manga.save(updated_by=self.user)

        response = self.client.post(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]))
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]))

    def test_manga_dmca_request_view_post_invalid(self):
        response = self.client.post(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca-request.html')

    def test_manga_dmca_request_view_post(self):
        response = self.client.post(reverse('manga.dmca.request', args=[self.manga.id, self.manga.slug]), {
            'check1': 'on',
            'check2': 'on',
        })
        self.assertRedirects(response, reverse('manga', args=[self.manga.id, self.manga.slug]))

        manga = Manga.all.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.DMCA)


class MangaDmcaTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.manga.status = MangaStatus.DMCA
        self.manga.save(self.user)

        self.user.is_staff = False
        self.user.save()

    def test_manga_view_get(self):
        response = self.client.get(reverse('manga', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_thumbnails_view_get(self):
        response = self.client.get(reverse('manga.thumbnails', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_download_view_post(self):
        response = self.client.post(reverse('manga.download', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_report_view_get(self):
        response = self.client.get(reverse('manga.report', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_report_view_post(self):
        response = self.client.post(reverse('manga.report', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_favorite_view_post(self):
        response = self.client.post(reverse('manga.favorite', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_edit_view_get(self):
        response = self.client.get(reverse('manga.edit', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_edit_view_post(self):
        response = self.client.post(reverse('manga.edit', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_edit_images_view_get(self):
        response = self.client.get(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_edit_images_view_post(self):
        response = self.client.post(reverse('manga.edit.images', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_edit_images_page_view_get(self):
        manga_page = self.manga.mangapage_set.all()[0]
        response = self.client.get(reverse('manga.edit.images.page', args=[self.manga.id, self.manga.slug, manga_page.page]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')

    def test_manga_edit_upload_view_post(self):
        response = self.client.post(reverse('manga.edit.upload', args=[self.manga.id, self.manga.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manga/manga-dmca.html')
