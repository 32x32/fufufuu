import os
from django.core.files.uploadedfile import SimpleUploadedFile
from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.enums import MangaCategory, MangaStatus
from fufufuu.manga.forms import MangaEditForm
from fufufuu.manga.models import MangaTag, Manga, MangaPage
from fufufuu.manga.views import MangaEditImagesView
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


class MangaPageFormsetTests(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.page1 = MangaPage.objects.get(manga=self.manga)
        self.page2 = MangaPage.objects.create(manga=self.manga, page=2)
        self.page3 = MangaPage.objects.create(manga=self.manga, page=3)

    def test_manga_page_formset_unselected_forms(self):
        formset = MangaEditImagesView.get_formset_cls()(
            user=self.user,
            queryset=MangaPage.objects.filter(manga=self.manga),
            data={
                'form-TOTAL_FORMS': '3',
                'form-INITIAL_FORMS': '3',
                'form-MAX_NUM_FORMS': '100',
                'form-0-id': self.page1.id,
                'form-0-ORDER': '1',
                'form-0-select': 'on',
                'form-1-id': self.page2.id,
                'form-1-ORDER': '2',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '3',
                'form-2-select': 'on',
                'action': 'reorder',
            },
        )
        self.assertTrue(formset.is_valid())
        self.assertEqual([f.instance for f in formset.unselected_forms], [self.page2])
        self.assertEqual([f.instance for f in formset.selected_forms], [self.page1, self.page3])

    def test_manga_page_formset_invalid_action(self):
        formset = MangaEditImagesView.get_formset_cls()(
            user=self.user,
            queryset=MangaPage.objects.filter(manga=self.manga),
            data={
                'form-TOTAL_FORMS': '3',
                'form-INITIAL_FORMS': '3',
                'form-MAX_NUM_FORMS': '100',
                'form-0-id': self.page1.id,
                'form-0-ORDER': '1',
                'form-1-id': self.page2.id,
                'form-1-ORDER': '2',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '3',
            },
        )
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(), ['The form was submitted without an action, please re-submit this form.'])

    def test_manga_page_formset_reorder(self):
        formset = MangaEditImagesView.get_formset_cls()(
            user=self.user,
            queryset=MangaPage.objects.filter(manga=self.manga),
            data={
                'form-TOTAL_FORMS': '3',
                'form-INITIAL_FORMS': '3',
                'form-MAX_NUM_FORMS': '100',
                'form-0-id': self.page1.id,
                'form-0-ORDER': '3',
                'form-1-id': self.page2.id,
                'form-1-ORDER': '1',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '2',
                'action': 'reorder',
            },
        )
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(MangaPage.objects.get(id=self.page1.id).page, 3)
        self.assertEqual(MangaPage.objects.get(id=self.page2.id).page, 1)
        self.assertEqual(MangaPage.objects.get(id=self.page3.id).page, 2)

    def test_manga_page_formset_set_cover_invalid(self):
        formset = MangaEditImagesView.get_formset_cls()(
            user=self.user,
            queryset=MangaPage.objects.filter(manga=self.manga),
            data={
                'form-TOTAL_FORMS': '3',
                'form-INITIAL_FORMS': '3',
                'form-MAX_NUM_FORMS': '100',
                'form-0-id': self.page1.id,
                'form-0-ORDER': '3',
                'form-1-id': self.page2.id,
                'form-1-ORDER': '1',
                'form-1-select': 'on',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '2',
                'form-2-select': 'on',
                'action': 'set_cover',
            },
        )
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(), ['Please select only a single image to set as the cover.'])

    def test_manga_page_formset_set_cover(self):
        self.page2.image = SimpleUploadedFile('sample.jpg', self.create_test_image_file().getvalue())
        self.page2.save()
        formset = MangaEditImagesView.get_formset_cls()(
            user=self.user,
            queryset=MangaPage.objects.filter(manga=self.manga),
            data={
                'form-TOTAL_FORMS': '3',
                'form-INITIAL_FORMS': '3',
                'form-MAX_NUM_FORMS': '100',
                'form-0-id': self.page1.id,
                'form-0-ORDER': '3',
                'form-1-id': self.page2.id,
                'form-1-ORDER': '1',
                'form-1-select': 'on',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '2',
                'action': 'set_cover',
            },
        )
        self.assertTrue(formset.is_valid())
        formset.save()
        self.assertEqual(MangaPage.objects.get(id=self.page1.id).page, 1)
        self.assertEqual(MangaPage.objects.get(id=self.page2.id).page, 2)
        self.assertEqual(MangaPage.objects.get(id=self.page3.id).page, 3)
        manga = Manga.objects.get(id=self.manga.id)
        self.assertNotEqual(manga.cover.path, self.page2.image.path)
        self.assertTrue(os.path.exists(manga.cover.path))

    def test_manga_page_formset_delete_invalid(self):
        pass

    def test_manga_page_formset_delete(self):
        pass
