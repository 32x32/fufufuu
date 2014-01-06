import json
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from fufufuu.core.languages import Language
from fufufuu.core.tests import BaseTestCase
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import TagData, TagDataHistory, Tag, TagAlias
from fufufuu.tag.utils import get_or_create_tag_by_name_or_alias


class TagModelTests(BaseTestCase):

    def test_tag_data_delete(self):
        tag_data = TagData.objects.all()[0]
        tag_data.cover = SimpleUploadedFile('sample.jpg', self.create_test_image_file().getvalue())
        tag_data.save(self.user)

        path = tag_data.cover.path
        self.assertTrue(os.path.exists(path))

        tag_data.delete()
        self.assertFalse(os.path.exists(path))

    def test_tag_data_history_delete(self):
        tag_data_history = TagDataHistory.objects.all()[0]
        tag_data_history.cover = SimpleUploadedFile('sample.jpg', self.create_test_image_file().getvalue())
        tag_data_history.save()

        path = tag_data_history.cover.path
        self.assertTrue(os.path.exists(path))

        tag_data_history.delete()
        self.assertFalse(os.path.exists(path))


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
        self.assertTemplateUsed(response, 'tag/tag-list-grid.html')

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
