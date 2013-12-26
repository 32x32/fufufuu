from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.enums import MangaCategory
from fufufuu.manga.forms import MangaEditForm
from fufufuu.manga.models import MangaTag
from fufufuu.tag.enums import TagType


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
        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
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

    def test_manga_edit_form_tag_limit(self):
        pass

    def test_manga_edit_form_tank_and_collection(self):
        pass

    def test_manga_edit_form_tags(self):
        pass

    def test_manga_edit_form_cover_required(self):
        pass
