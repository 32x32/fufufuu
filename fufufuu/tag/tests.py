import os
from io import BytesIO
from django.core.files.base import File
from django.core.urlresolvers import reverse
from fufufuu.core.tests import BaseTestCase
from fufufuu.tag.models import TagData, TagDataHistory


class TagModelTests(BaseTestCase):

    def test_tag_data_delete(self):
        tag_data = TagData.objects.all()[0]
        tag_data.cover.save('sample-file.jpg', File(BytesIO()), save=False)
        tag_data.save(self.user)

        path = tag_data.cover.path
        self.assertTrue(os.path.exists(path))

        tag_data.delete()
        self.assertFalse(os.path.exists(path))

    def test_tag_data_history_delete(self):
        tag_data_history = TagDataHistory.objects.all()[0]
        tag_data_history.cover.save('sample-file.jpg', File(BytesIO()), save=False)
        tag_data_history.save()

        path = tag_data_history.cover.path
        self.assertTrue(os.path.exists(path))

        tag_data_history.delete()
        self.assertFalse(os.path.exists(path))


class TagListViewTests(BaseTestCase):

    def test_tag_list_view_get_authors(self):
        response = self.client.get(reverse('tag.list', args=['authors']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_circles(self):
        response = self.client.get(reverse('tag.list', args=['circles']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_collections(self):
        response = self.client.get(reverse('tag.list', args=['collections']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list-collection.html')

    def test_tag_list_view_get_content(self):
        response = self.client.get(reverse('tag.list', args=['content']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_events(self):
        response = self.client.get(reverse('tag.list', args=['events']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_magazines(self):
        response = self.client.get(reverse('tag.list', args=['magazines']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_parodies(self):
        response = self.client.get(reverse('tag.list', args=['parodies']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_scanlators(self):
        response = self.client.get(reverse('tag.list', args=['scanlators']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list.html')

    def test_tag_list_view_get_tanks(self):
        response = self.client.get(reverse('tag.list', args=['tanks']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tag/tag-list-tank.html')

    def test_tag_list_view_get_unknown_type(self):
        response = self.client.get(reverse('tag.list', args=['unknown']))
        self.assertEqual(response.status_code, 404)
