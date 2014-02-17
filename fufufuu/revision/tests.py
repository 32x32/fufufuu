import copy

from django.core.files.uploadedfile import SimpleUploadedFile

from fufufuu.core.tests import BaseTestCase
from fufufuu.revision.models import Revision
from fufufuu.tag.enums import TagType
from fufufuu.tag.models import Tag


class RevisionModelTests(BaseTestCase):

    def test_revision_create(self):
        old_manga = self.manga
        new_manga = copy.deepcopy(self.manga)

        old_manga.cover = None
        new_manga.cover = SimpleUploadedFile('test.png', self.create_test_image_file().getvalue())
        new_manga.save(updated_by=self.user)

        old_manga.title = 'Old Title'
        new_manga.title = 'New Title'
        old_manga.slug = 'old-title'
        new_manga.slug = 'new-title'
        old_manga.uncensored = False
        new_manga.uncensored = True

        revision = Revision.create(old_manga, new_manga, self.user)
        self.assertEqual(revision.created_by, self.user)
        self.assertEqual(revision.diff, {
            'title': ('Old Title', 'New Title'),
            'uncensored': (False, True),
            'cover': (old_manga.cover, new_manga.cover),
        })

    def test_revision_create_foreign_key(self):
        old_manga = self.manga
        new_manga = copy.deepcopy(self.manga)

        tank = Tag.objects.filter(tag_type=TagType.TANK)[0]
        old_manga.tank = None
        new_manga.tank = tank

        collection = Tag.objects.filter(tag_type=TagType.COLLECTION)[0]
        old_manga.collection = None
        new_manga.collection = collection

        revision = Revision.create(old_manga, new_manga, self.user)
        self.assertEqual(revision.created_by, self.user)
        self.assertEqual(revision.diff, {
            'tank': (None, tank.id),
            'collection': (None, collection.id),
        })

    def test_revision_create_m2m(self):
        old_manga = self.manga
        new_manga = copy.deepcopy(self.manga)

        tag_list = list(Tag.objects.all())

        import random
        tag_list = random.sample(tag_list, 2)
        old_tags = tag_list[:1]
        new_tags = tag_list[1:]

        old_manga.tags.clear()
        old_manga.tags.add(*old_tags)

        revision = Revision.create(old_manga, new_manga, self.user, m2m_data={
            'tags': [t.id for t in new_tags],
        })
        actual_old_tags, actual_new_tags = revision.diff['tags']
        self.assertEqual(
            (set(actual_old_tags), set(actual_new_tags)),
            (set([t.id for t in old_tags]), set([t.id for t in new_tags])),
        )

    def test_revision_create_m2m_identical(self):
        old_manga = self.manga
        new_manga = copy.deepcopy(self.manga)

        tag_list = list(Tag.objects.all())

        import random
        old_tags = random.sample(tag_list, 1)

        old_manga.tags.clear()
        old_manga.tags.add(*old_tags)

        revision = Revision.create(old_manga, new_manga, self.user, m2m_data={
            'tags': [t.id for t in old_tags],
        })
        self.assertEquals(revision, None)

    def test_revision_create_no_changes(self):
        old_manga = self.manga
        new_manga = copy.deepcopy(self.manga)

        revision = Revision.create(old_manga, new_manga, self.user)
        self.assertEqual(revision, None)
