import copy

from django.core.files.uploadedfile import SimpleUploadedFile

from fufufuu.core.tests import BaseTestCase
from fufufuu.manga.models import Manga
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
        tag_list = random.sample(tag_list, 4)
        old_tags = tag_list[:2]
        new_tags = tag_list[2:]

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
        self.assertEqual(revision, None)

    def test_revision_create_no_changes(self):
        old_manga = self.manga
        new_manga = copy.deepcopy(self.manga)

        revision = Revision.create(old_manga, new_manga, self.user)
        self.assertEqual(revision, None)


class RevisionEventModelTests(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.old_manga = self.manga
        self.new_manga = copy.deepcopy(self.manga)

        self.old_manga.cover = None
        self.new_manga.cover = SimpleUploadedFile('test.png', self.create_test_image_file().getvalue())
        self.new_manga.save(updated_by=self.user)

        self.old_manga.title = 'Old Title'
        self.new_manga.title = 'New Title'
        self.old_manga.uncensored = False
        self.new_manga.uncensored = True

        self.tank = Tag.objects.filter(tag_type=TagType.TANK)[0]
        self.old_manga.tank = self.tank
        self.new_manga.tank = None

        self.collection = Tag.objects.filter(tag_type=TagType.COLLECTION)[0]
        self.old_manga.collection = None
        self.new_manga.collection = self.collection

        import random
        tag_list = list(Tag.objects.all())
        tag_list = random.sample(tag_list, 4)
        self.old_tags = tag_list[:2]
        self.new_tags = tag_list[2:]

        self.old_manga.tags.clear()
        self.old_manga.tags.add(*self.old_tags)

        self.revision = Revision.create(self.old_manga, self.new_manga, self.user, m2m_data={
            'tags': [t.id for t in self.new_tags],
        })

    def test_revision_revert(self):
        self.new_manga.save(self.user)
        self.new_manga.tags.clear()
        self.new_manga.tags.add(*self.new_tags)

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(set(manga.tags.all()), set(self.new_tags))

        manga = self.revision.revert()
        self.assertEqual(manga.title, 'Old Title')
        self.assertEqual(manga.slug, 'new-title')
        self.assertFalse(manga.uncensored)
        self.assertFalse(manga.cover)
        self.assertEqual(set(manga.tags.all()), set(self.old_tags))
        self.assertEqual(manga.collection, None)
        self.assertEqual(manga.tank, self.tank)

    def test_revision_apply(self):
        self.old_manga.save(self.user)
        self.old_manga.tags.clear()
        self.old_manga.tags.add(*self.old_tags)

        manga = Manga.objects.get(id=self.manga.id)
        self.assertEqual(set(manga.tags.all()), set(self.old_tags))

        manga = self.revision.apply()
        self.assertEqual(manga.title, 'New Title')
        self.assertEqual(manga.slug, 'old-title')
        self.assertTrue(manga.uncensored)
        self.assertTrue(manga.cover)
        self.assertEqual(set(manga.tags.all()), set(self.new_tags))
        self.assertEqual(manga.collection, self.collection)
        self.assertEqual(manga.tank, None)
