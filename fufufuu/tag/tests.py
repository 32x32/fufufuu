import os
from io import BytesIO
from django.core.files.base import File
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
