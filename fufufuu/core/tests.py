from itertools import permutations
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

from fufufuu.account.models import User
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.filters import exclude_keys
from fufufuu.core.models import DeletedFile, SiteSetting
from fufufuu.core.utils import slugify, convert_markdown, natural_sort
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
        super().setUp()

        cache.clear()

        User.set_password = fast_set_password
        User.check_password = fast_check_password

        self.user = User.objects.get(username='testuser')
        self.user.set_password('password')
        self.user.save()

        self.manga = Manga.published.latest('published_on')

        self.request = namedtuple('Request', 'user')
        self.request.user = self.user
        self.request.META = {'REMOTE_ADDR': '127.0.0.1'}
        self.client.login(username='testuser', password='password')

    def assertTemplateUsed(self, response, template_name):
        self.assertEqual(response.template_name, template_name)

    def create_test_image_file(self, width=800, height=1200, format='PNG'):
        image_file = BytesIO()
        img = Image.new('RGB', (width, height))
        img.save(image_file, format=format)
        return image_file

    def create_test_user(self, username):
        user = User(username=username)
        user.set_password('password')
        user.save()
        return user


class CoreUtilTests(BaseTestCase):

    def test_slugify(self):
        self.assertEqual(slugify('北京'), 'bei-jing')
        self.assertEqual(slugify('~'), '')

    def test_natural_sort(self):
        class TestObj:
            def __init__(self, value): self.value = value

        expected_list = [
            TestObj('5'),
            TestObj('007'),
            TestObj('08'),
            TestObj('9'),
            TestObj('10'),
            TestObj('011'),
            TestObj('12'),
        ]

        for test_list in permutations(expected_list):
            self.assertEqual(natural_sort(test_list, 'value'), expected_list)

    def test_convert_markdown_empty(self):
        self.assertEqual(convert_markdown('   '), '')

    def test_convert_markdown_simple(self):
        self.assertEqual(convert_markdown('abc'), '<p>abc</p>')

    def test_convert_markdown_raw_html(self):
        markdown = '<script type="text/javascript>alert("woops!");</script>'
        expected_html = '<p>&lt;script type="text/javascript&gt;alert("woops!");&lt;/script&gt;</p>'
        self.assertEqual(convert_markdown(markdown), expected_html)

    def test_convert_markdown_images(self):
        markdown = '![Google Logo](http://localhost:8000/static/images/no-avatar.png)'
        expected_html = '<p>![Google Logo](http://localhost:8000/static/images/no-avatar.png)</p>'
        self.assertEqual(convert_markdown(markdown), expected_html)


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

    def test_deleted_files_clear(self):
        self.assertTrue(os.path.exists(self.file.name))

        call_command('clear_deleted_files')
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


class CoreModelTests(BaseTestCase):

    def test_site_setting_as_dict(self):
        SiteSetting.set_val(SiteSettingKey.DOWNLOAD_LIMIT, '1000', self.user)

        d = SiteSetting.as_dict()
        self.assertEqual(d.get(SiteSettingKey.ENABLE_COMMENTS),True)
        self.assertEqual(d.get(SiteSettingKey.DOWNLOAD_LIMIT), 1000)

    def test_site_setting_set_val(self):
        SiteSetting.set_val(SiteSettingKey.DOWNLOAD_LIMIT, '1000', self.user)
        self.assertEqual(SiteSetting.get_val(SiteSettingKey.DOWNLOAD_LIMIT), 1000)

    def test_site_setting_get_val_default(self):
        SiteSetting.objects.all().delete()
        for key in SiteSettingKey.choices_dict.keys():
            self.assertEqual(SiteSetting.get_val(key), SiteSettingKey.default[key], key)

    def test_site_setting_keys(self):
        choices_keys = set(SiteSettingKey.choices_dict.keys())
        key_type_keys = set(SiteSettingKey.key_type.keys())
        form_field_type_keys = set(SiteSettingKey.form_field_type.keys())
        default_keys = set(SiteSettingKey.default.keys())

        self.assertEqual(choices_keys, key_type_keys)
        self.assertEqual(key_type_keys, form_field_type_keys)
        self.assertEqual(form_field_type_keys, default_keys)
