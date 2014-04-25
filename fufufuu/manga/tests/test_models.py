import os
from io import BytesIO

from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile

from fufufuu.core.tests import BaseTestCase
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.models import Image
from fufufuu.manga.enums import MangaStatus
from fufufuu.manga.models import Manga, MangaPage, MangaArchive
from fufufuu.tag.models import Tag


class MangaModelTests(BaseTestCase):

    def test_manga_save_slugify(self):
        manga = Manga(title='Some Brand New Title')
        manga.save(updated_by=self.user)
        self.assertEqual(manga.slug, 'some-brand-new-title')

    def test_manga_delete_draft(self):
        manga = Manga(status=MangaStatus.DRAFT)
        manga.save(updated_by=self.user)
        manga.delete()
        self.assertFalse(Manga.all.filter(id=manga.id).exists())

    def test_manga_delete_force_delete(self):
        self.assertEqual(self.manga.status, MangaStatus.PUBLISHED)
        self.manga.delete(force_delete=True)
        self.assertFalse(Manga.all.filter(id=self.manga.id).exists())

    def test_manga_delete(self):
        self.assertEqual(self.manga.status, MangaStatus.PUBLISHED)
        self.manga.delete(updated_by=self.user)
        manga = Manga.all.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.DELETED)

    def test_manga_page_delete(self):
        mp = MangaPage(
            manga=self.manga,
            page=1,
            image=SimpleUploadedFile('sample.jpg', self.create_test_image_file().getvalue())
        )
        mp.save()

        path = mp.image.path
        self.assertTrue(os.path.exists(path))

        mp.delete()
        self.assertFalse(os.path.exists(path))

    def test_manga_archive_delete(self):
        ma = MangaArchive(manga=self.manga)
        ma.file.save('sample-file.zip', File(BytesIO()), save=False)
        ma.save()

        path = ma.file.path
        self.assertTrue(os.path.exists(path))

        ma.delete()
        self.assertFalse(os.path.exists(path))

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

    def test_manga_post_save(self):
        self.manga.cover = SimpleUploadedFile('test.png', self.create_test_image_file().getvalue())
        self.manga.save(updated_by=self.user)

        image1 = Image(key_type=ImageKeyType.MANGA_COVER, key_id=self.manga.id)
        image1.save(self.manga.cover.path)

        self.manga.save(updated_by=self.user)
        self.assertFalse(Image.objects.filter(id=image1.id).exists())

    def test_manga_archive_name(self):
        author = Tag.objects.get(name='Author 1')
        circle = Tag.objects.get(name='Circle 1')
        scanlator = Tag.objects.get(name='Scanlator 1')

        manga = self.manga

        def assert_manga_archive_name(name, tags=None):
            manga.tags.clear()
            if tags:
                manga.tags.add(*tags)
            manga.update_tag_dictionary()
            self.assertEqual(manga.archive_name, name)

        assert_manga_archive_name('Test Manga 1.zip')
        assert_manga_archive_name('(Author 1) Test Manga 1.zip', [author])
        assert_manga_archive_name('[Circle 1] Test Manga 1.zip', [circle])
        assert_manga_archive_name('[Scanlator 1] Test Manga 1.zip', [scanlator])
        assert_manga_archive_name('[Scanlator 1][Circle 1 (Author 1)] Test Manga 1.zip', [author, circle, scanlator])

