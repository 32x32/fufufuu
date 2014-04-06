from django.core.urlresolvers import reverse
from fufufuu.blog.models import BlogEntry
from fufufuu.core.tests import BaseTestCase


class BlogEntryListViewTests(BaseTestCase):

    def test_blog_entry_list_view_get(self):
        response = self.client.get(reverse('blog.entry.list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-list.html')


class BlogEntryViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.blog_entry = BlogEntry.objects.first()

    def test_blog_entry_view_get(self):
        response = self.client.get(reverse('blog.entry', args=[self.blog_entry.id, self.blog_entry.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry.html')


class BlogEntryCreateViewTests(BaseTestCase):

    def test_blog_entry_create_view_get(self):
        response = self.client.get(reverse('blog.entry.create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-create.html')

    def test_blog_entry_create_view_post_invalid(self):
        pass

    def test_blog_entry_create_view_post(self):
        pass


class BlogEntryEditViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.blog_entry = BlogEntry.objects.first()

    def test_blog_entry_edit_view_get(self):
        response = self.client.get(reverse('blog.entry.edit', args=[self.blog_entry.id, self.blog_entry.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-edit.html')

    def test_blog_entry_edit_view_post_invalid(self):
        pass

    def test_blog_entry_edit_view_post(self):
        pass
