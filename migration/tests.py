from unittest.case import TestCase
from migrate import convert_text_to_markdown


class MigratorTests(TestCase):

    def test_migrator_convert_text_to_markdown_newline(self):
        markdown_raw = 'Hello\nWorld'
        self.assertEqual(convert_text_to_markdown(markdown_raw), 'Hello\n\nWorld')

    def test_migrator_convert_text_to_markdown_url(self):
        markdown_raw = 'http://www.google.com'
        self.assertEqual(convert_text_to_markdown(markdown_raw), '[http://www.google.com](http://www.google.com)')
