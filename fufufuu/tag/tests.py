import json
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import TagData, Tag, TagAlias
from fufufuu.tag.utils import get_or_create_tag_by_name_or_alias


class TagModelTests(BaseTestCase):

    def test_tag_delete(self):
        tag = Tag.objects.all()[0]
        tag.cover = SimpleUploadedFile('sample.jpg', self.create_test_image_file().getvalue())
        tag.save(self.user)

        path = tag.cover.path
        self.assertTrue(os.path.exists(path))

        tag.delete()
        self.assertFalse(os.path.exists(path))

    def test_tag_set_default_cover_author(self):
        tag = Tag.objects.filter(tag_type=TagType.AUTHOR)[0]
        tag.set_default_cover()
        self.assertFalse(tag.cover)

    def test_tag_set_default_cover_tank_no_manga(self):
        tag = Tag.objects.filter(tag_type=TagType.TANK)[0]
        tag.manga_set.all().delete()
        tag.set_default_cover()
        self.assertFalse(tag.cover)

    def test_tag_set_default_cover_tank(self):
        tag = Tag.objects.filter(tag_type=TagType.TANK)[0]
        self.assertFalse(tag.cover)

        self.manga.tank = tag
        self.manga.cover = SimpleUploadedFile('test', self.create_test_image_file().getvalue())
        self.manga.save(self.user)

        tag.set_default_cover()
        self.assertTrue(tag.cover)

    def test_tag_set_default_cover_collection(self):
        tag = Tag.objects.filter(tag_type=TagType.COLLECTION)[0]
        self.assertFalse(tag.cover)

        self.manga.collection = tag
        self.manga.cover = SimpleUploadedFile('test', self.create_test_image_file().getvalue())
        self.manga.save(self.user)

        tag.set_default_cover()
        self.assertTrue(tag.cover)


class TagListViewTests(BaseTestCase):

    def test_tag_list_view_get_authors(self):
        response = self.client.get(reverse('tag.list.author'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_circles(self):
        response = self.client.get(reverse('tag.list.circle'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_collections(self):
        response = self.client.get(reverse('tag.list.collection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_content(self):
        response = self.client.get(reverse('tag.list.content'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_events(self):
        response = self.client.get(reverse('tag.list.event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_magazines(self):
        response = self.client.get(reverse('tag.list.magazine'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_parodies(self):
        response = self.client.get(reverse('tag.list.parody'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_scanlators(self):
        response = self.client.get(reverse('tag.list.scanlator'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_tanks(self):
        response = self.client.get(reverse('tag.list.tank'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_grid_view_get_collections(self):
        response = self.client.get(reverse('tag.list.grid.collection'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list-grid.html')

    def test_tag_list_grid_view_get_tanks(self):
        response = self.client.get(reverse('tag.list.grid.tank'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list-grid.html')


class TagAutocompleteViewTests(BaseTestCase):

    def test_tag_autocomplete_view_get_not_ajax(self):
        response = self.client.get(reverse('tag.autocomplete'))
        self.assertEqual(response.status_code, 404)

    def test_tag_autocomplete_view_get(self):
        response = self.client.get(
            reverse('tag.autocomplete'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        tag_dict = json.loads(response.content.decode('utf-8'))
        for tag_type in TagType.choices_dict:
            self.assertTrue(tag_type in tag_dict, '{} not in tag_dict'.format(tag_type))


class TagViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.tag = Tag.objects.all()[0]

    def test_tag_view_get(self):
        response = self.client.get(reverse('tag', args=[self.tag.id, self.tag.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag.html')


class TagUtilTests(BaseTestCase):

    def test_get_or_create_tag_by_name_or_alias_in_tag(self):
        expected_tag = Tag.objects.all()[0]
        actual_tag = get_or_create_tag_by_name_or_alias(expected_tag.tag_type, expected_tag.name, self.user)
        self.assertEqual(expected_tag, actual_tag)

    def test_get_or_create_tag_by_name_or_alias_in_alias(self):
        expected_tag = Tag.objects.all()[0]
        TagAlias.objects.create(tag=expected_tag, language=Language.ENGLISH, name='Test Alias')
        actual_tag = get_or_create_tag_by_name_or_alias(expected_tag.tag_type, 'Test Alias', self.user)
        self.assertEqual(expected_tag, actual_tag)

    def test_get_or_create_tag_by_name_or_alias_create(self):
        self.assertFalse(Tag.objects.filter(tag_type=TagType.AUTHOR, name='Test Tag').exists())
        tag = get_or_create_tag_by_name_or_alias(TagType.AUTHOR, 'Test Tag', self.user)
        self.assertEqual(tag.tag_type, TagType.AUTHOR)
        self.assertEqual(tag.name, 'Test Tag')
        self.assertEqual(tag.slug, 'test-tag')
        self.assertEqual(tag.updated_by, self.user)
        self.assertEqual(tag.created_by, self.user)
