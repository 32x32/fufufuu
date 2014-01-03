from collections import namedtuple
from io import BytesIO
from PIL import Image
from django.core.management import call_command
from django.db import connections
from django.test.runner import DiscoverRunner
from django.test.testcases import TestCase
from fufufuu.account.models import User
from fufufuu.core.utils import slugify
from fufufuu.datacreator import DataCreator
from fufufuu.manga.models import Manga


def fast_set_password(self, raw_password):
    self.password = raw_password

def fast_check_password(self, raw_password):
    return self.password == raw_password


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
        pass


class BaseTestCase(TestCase):

    def setUp(self):
        super().setUp()

        User.set_password = fast_set_password
        User.check_password = fast_check_password

        self.user = User.objects.get(username='testuser')
        self.user.set_password('password')
        self.user.save()

        self.request = namedtuple('Request', 'user')
        self.request.user = self.user

        self.manga = Manga.published.latest('published_on')

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
