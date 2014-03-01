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
        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'authors': ', '.join(['Author {}'.format(i) for i in range(100)]),
            'action': 'save',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['Exceeded maximum number of allowed tags that can be assigned.'])

    def test_manga_edit_form_tank_and_collection(self):
        tank = Tag.objects.filter(tag_type=TagType.TANK)[0]
        collection = Tag.objects.filter(tag_type=TagType.COLLECTION)[0]
        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'tank': tank.name,
            'tank_chapter': '2',
            'collection': collection.name,
            'collection_part': '3',
            'action': 'save',
        })
        self.assertTrue(form.is_valid())
        form.save()

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.tank, tank)
        self.assertEqual(manga.tank_chapter, '2')
        self.assertEqual(manga.collection, collection)
        self.assertEqual(manga.collection_part, '3')

    def test_manga_edit_form_tags(self):
        authors = Tag.objects.filter(tag_type=TagType.AUTHOR)
        circles = Tag.objects.filter(tag_type=TagType.CIRCLE)
        content = Tag.objects.filter(tag_type=TagType.CONTENT)
        events = Tag.objects.filter(tag_type=TagType.EVENT)
        magazines = Tag.objects.filter(tag_type=TagType.MAGAZINE)
        parodies = Tag.objects.filter(tag_type=TagType.PARODY)
        scanlators = Tag.objects.filter(tag_type=TagType.SCANLATOR)

        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'authors': ', '.join([t.name for t in authors]),
            'circles': ', '.join([t.name for t in circles]),
            'content': ', '.join([t.name for t in content]),
            'events': ', '.join([t.name for t in events]),
            'magazines': ', '.join([t.name for t in magazines]),
            'parodies': ', '.join([t.name for t in parodies]),
            'scanlators': ', '.join([t.name for t in scanlators]),
            'action': 'save',
        })
        self.assertTrue(form.is_valid())
        form.save()

        manga = Manga.objects.get(id=self.manga.id)
        tag_dictionary = manga.tag_dictionary

        self.assertEqual(set(tag_dictionary[TagType.AUTHOR]), set(authors))
        self.assertEqual(set(tag_dictionary[TagType.CIRCLE]), set(circles))
        self.assertEqual(set(tag_dictionary[TagType.CONTENT]), set(content))
        self.assertEqual(set(tag_dictionary[TagType.EVENT]), set(events))
        self.assertEqual(set(tag_dictionary[TagType.MAGAZINE]), set(magazines))
        self.assertEqual(set(tag_dictionary[TagType.PARODY]), set(parodies))
        self.assertEqual(set(tag_dictionary[TagType.SCANLATOR]), set(scanlators))

    def test_manga_edit_form_cover_update(self):
        self.manga.cover = SimpleUploadedFile('test1.jpg', self.create_test_image_file().getvalue())
        self.manga.save(self.user)
        old_cover_path = self.manga.cover.path

        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': 'Test Manga Title',
            'category': MangaCategory.VANILLA,
            'language': Language.ENGLISH,
            'action': 'save',
        }, files={
            'cover': SimpleUploadedFile('test2.jpg', self.create_test_image_file().getvalue())
        })
        self.assertTrue(form.is_valid())
        form.save()

        manga = Manga.objects.get(id=self.manga.id)
        new_cover_path = manga.cover.path
        self.assertNotEqual(old_cover_path, new_cover_path)

    def test_manga_edit_form_no_changes(self):
        data = {
            'title':        self.manga.title,
            'category':     self.manga.category,
            'language':     self.manga.language,
            'markdown':     self.manga.markdown,
            'authors':      ', '.join([t.name for t in self.manga.tag_dictionary[TagType.AUTHOR]]),
            'circles':      ', '.join([t.name for t in self.manga.tag_dictionary[TagType.CIRCLE]]),
            'content':      ', '.join([t.name for t in self.manga.tag_dictionary[TagType.CONTENT]]),
            'events':       ', '.join([t.name for t in self.manga.tag_dictionary[TagType.EVENT]]),
            'magazines':    ', '.join([t.name for t in self.manga.tag_dictionary[TagType.MAGAZINE]]),
            'parodies':     ', '.join([t.name for t in self.manga.tag_dictionary[TagType.PARODY]]),
            'scanlators':   ', '.join([t.name for t in self.manga.tag_dictionary[TagType.SCANLATOR]]),
            'action':       'save',
        }
        form = MangaEditForm(request=self.request, instance=self.manga, data=data)
        self.assertTrue(form.is_valid())
        form.save()

    def test_manga_edit_form_markdown_utf8(self):
        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': self.manga.title,
            'category': self.manga.category,
            'language': self.manga.language,
            'markdown': '北京',
            'action': 'save',
        })
        self.assertTrue(form.is_valid())
        form.save()

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(manga.markdown, '北京')

    def test_manga_edit_form_edit_limit(self):
        user = self.create_test_user('testuser2')
        user.revision_limit = 0
        self.client.login(username='testuser2', password='password')

        self.request.user = user

        form = MangaEditForm(request=self.request, instance=self.manga, data={
            'title': self.manga.title,
            'language': self.manga.language,
            'category': self.manga.category,
            'action': 'save',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['You have reached your edit limit for the day, please try again later.'])


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
        formset.save(self.manga)
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
        formset.save(self.manga)
        self.assertEqual(MangaPage.objects.get(id=self.page1.id).page, 1)
        self.assertEqual(MangaPage.objects.get(id=self.page2.id).page, 2)
        self.assertEqual(MangaPage.objects.get(id=self.page3.id).page, 3)
        manga = Manga.objects.get(id=self.manga.id)
        self.assertNotEqual(manga.cover.path, self.page2.image.path)
        self.assertTrue(os.path.exists(manga.cover.path))

    def test_manga_page_formset_delete_non_selected(self):
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
                'action': 'delete',
            },
        )
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(), ['Please select at least one image to delete.'])

    def test_manga_page_formset_delete_all_selected(self):
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
                'form-1-select': 'on',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '3',
                'form-2-select': 'on',
                'action': 'delete',
            },
        )
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors(), ['Please leave at least one image in this upload undeleted.'])

    def test_manga_page_formset_delete(self):
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
                'form-1-select': 'on',
                'form-2-id': self.page3.id,
                'form-2-ORDER': '3',
                'action': 'delete',
            },
        )
        self.assertTrue(formset.is_valid())
        formset.save(self.manga)

        self.assertEqual(MangaPage.objects.get(id=self.page1.id).page, 1)
        self.assertEqual(MangaPage.objects.get(id=self.page3.id).page, 2)
        self.assertFalse(MangaPage.objects.filter(id=self.page2.id).exists())
