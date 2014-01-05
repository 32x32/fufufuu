from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.manga.forms import MangaEditForm
from fufufuu.manga.models import MangaTag, Manga
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


class MangaEditFormTests(BaseTestCase):

    def test_manga_edit_form_missing_instance(self):
        try:
            MangaEditForm(request=self.request)
            self.fail('A RuntimeError should have been raised.')
        except RuntimeError as e:
            self.assertEqual(str(e), 'MangaEditForm must be used with an existing Manga instance.')

    def test_manga_edit_form_basic_initial(self):
        author_list = MangaTag.objects.filter(manga=self.manga, tag__tag_type=TagType.AUTHOR).values_list('tag__name', flat=True)
        form = MangaEditForm(request=self.request, instance=self.manga)
        self.assertEqual(form.fields['authors'].initial, ', '.join(sorted(author_list)))

    def test_manga_edit_form_basic(self):
        self.manga.tank = Tag.objects.filter(tag_type=TagType.TANK)[0]
        self.manga.tank_chapter = '1'
        self.manga.save(updated_by=self.user)

        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'save',
        })
        self.assertTrue(form.is_valid())
        manga = form.save()

        self.assertEqual(manga.category, MangaCategory.VANILLA)
        self.assertEqual(manga.language, Language.ENGLISH)
        self.assertEqual(manga.title, 'Test Manga Title')
        self.assertFalse(manga.tank)
        self.assertFalse(manga.tank_chapter)
        self.assertFalse(manga.collection)
        self.assertFalse(manga.collection_part)

    def test_manga_edit_form_already_published(self):
        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'action': 'publish',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['action'], ['This upload cannot be published.'])

    def test_manga_edit_form_publish_no_page(self):
        self.manga.mangapage_set.all().delete()
        self.manga.status = MangaStatus.DRAFT
        self.manga.save(updated_by=self.user)

        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'action': 'publish',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['action'], ['Please upload at least one image before publishing.'])

    def test_manga_edit_form_publish(self):
        self.manga.status = MangaStatus.DRAFT
        self.manga.published_on = None
        self.manga.save(updated_by=self.user)

        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'publish',
        })
        self.assertTrue(form.is_valid())
        form.save()

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.status, MangaStatus.PUBLISHED)
        self.assertTrue(manga.published_on)

    def test_manga_edit_form_tag_limit(self):
        pass

    def test_manga_edit_form_tank_and_collection(self):
        pass

    def test_manga_edit_form_tags(self):
        pass

    def test_manga_edit_form_cover_required(self):
        pass

    def test_manga_edit_form_cover_update(self):
        pass
