import os
import shutil
import sys
import tempfile
from collections import namedtuple
from io import BytesIO
from PIL import Image
from django.core.cache import cache
from django.core.management import call_command
from django.db import connections
from django.http.request import QueryDict
from django.test.runner import DiscoverRunner
from django.test.testcases import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from fufufuu import settings
from fufufuu.account.models import User
from fufufuu.core.filters import exclude_keys
from fufufuu.core.models import DeletedFile
from fufufuu.core.utils import slugify
from fufufuu.datacreator import DataCreator
from fufufuu.manga.models import Manga
from fufufuu.settings import BASE_DIR


MEDIA_ROOT = os.path.join(BASE_DIR, 'media-test')


def fast_set_password(self, raw_password):
    self.password = raw_password

def fast_check_password(self, raw_password):
    return self.password == raw_password


def suppress_output(f):
    def _suppress_output(*args, **kwargs):
        devnull = open(os.devnull, 'w')
        stdout, sys.stdout = sys.stdout, devnull
        f(*args, **kwargs)
        sys.stdout = stdout

    return _suppress_output


class FufufuuTestSuiteRunner(DiscoverRunner):

    def create_testdb(self):
        call_command('syncdb', interactive=False)
        dc = DataCreator('test')
        dc.run()

    def setup_databases(self, **kwargs):
        for alias in connections:
            connection = connections[alias]
            connection.settings_dict['NAME'] = ':memory:'
            self.create_testdb()

    def teardown_databases(self, old_config, **kwargs):
        try:
            shutil.rmtree(MEDIA_ROOT)
        except FileNotFoundError:
            pass


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class BaseTestCase(TestCase):

    def setUp(self):
        cache.clear()
        settings.DEBUG = False

        super().setUp()

        User.set_password = fast_set_password
        User.check_password = fast_check_password

        self.user = User.objects.get(username='testuser')
        self.user.set_password('password')
        self.user.save()

        self.manga = Manga.published.latest('published_on')

        self.request = namedtuple('Request', 'user')
        self.request.user = self.user
        self.client.login(username='testuser', password='password')

    def assertTemplateUsed(self, response, template_name):
        self.assertEqual(response.template_name, template_name)

    def create_test_image_file(self, width=800, height=1200, format='PNG'):
        image_file = BytesIO()
        img = Image.new('RGB', (width, height))
        img.save(image_file, format=format)
        return image_file


class CoreUtilTests(BaseTestCase):

    def test_slugify(self):
        self.assertEqual(slugify('北京'), 'bei-jing')
        self.assertEqual(slugify('~'), '')


class CoreManagementTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.file = tempfile.NamedTemporaryFile(delete=False)
        self.deleted_file1 = DeletedFile.objects.create(
            path='path-to-fake-file',
            delete_after=timezone.now() - timezone.timedelta(hours=1),
        )
        self.deleted_file2 = DeletedFile.objects.create(
            path='path-to-fake-file',
            delete_after=timezone.now() + timezone.timedelta(hours=1),
        )
        self.deleted_file3 = DeletedFile.objects.create(
            path=self.file.name,
            delete_after=timezone.now() - timezone.timedelta(hours=1),
        )


    def tearDown(self):
        super().tearDown()

    @suppress_output
    def test_deleted_files_info(self):
        call_command('deleted_files', 'info')

    def test_deleted_files_clear(self):
        self.assertTrue(os.path.exists(self.file.name))

        call_command('deleted_files', 'clear')
        self.assertFalse(DeletedFile.objects.filter(id=self.deleted_file1.id).exists())
        self.assertFalse(DeletedFile.objects.filter(id=self.deleted_file3.id).exists())
        self.assertTrue(DeletedFile.objects.filter(id=self.deleted_file2.id).exists())

        self.assertFalse(os.path.exists(self.file.name))


class CoreFilterTests(BaseTestCase):

    def test_exclude_keys(self):
        qd = QueryDict('a=1&b=2')
        self.assertEqual(exclude_keys(qd), QueryDict('a=1&b=2'))

    def test_exclude_keys_single_exclude(self):
        qd = QueryDict('a=1&b=2')
        self.assertEqual(exclude_keys(qd, 'b'), QueryDict('a=1'))

    def test_exclude_keys_multiple_excludes(self):
        qd = QueryDict('a=1&b=2&c=3')
        self.assertEqual(exclude_keys(qd, 'a', 'b'), QueryDict('c=3'))

    def test_exclude_keys_bad_exclude(self):
        qd = QueryDict('a=1&b=2')
        self.assertEqual(exclude_keys(qd, 'c'), QueryDict('a=1&b=2'))

    def test_exclude_keys_long_names(self):
        qd = QueryDict('abc=1&page=2')
        self.assertEqual(exclude_keys(qd, 'page'), QueryDict('abc=1'))
