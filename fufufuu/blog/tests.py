from django.core.urlresolvers import reverse
from fufufuu.blog.models import BlogEntry
from fufufuu.core.tests import BaseTestCase
from fufufuu.core.utils import slugify


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


class BlogEntryEditViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.blog_entry = BlogEntry.objects.first()

    def test_blog_entry_create_view_get(self):
        response = self.client.get(reverse('blog.entry.create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-edit.html')

    def test_blog_entry_create_view_post_invalid(self):
        response = self.client.post(reverse('blog.entry.create'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-edit.html')

    def test_blog_entry_create_view_post(self):
        response = self.client.post(reverse('blog.entry.create'), {
            'title': 'This is a sample post title',
            'markdown': 'Sample post content goes here!',
            'html': '<p>Sample post content goes here!</p>',
        })
        blog_entry = BlogEntry.objects.latest('created_on')
        self.assertRedirects(response, reverse('blog.entry.edit', args=[blog_entry.id, blog_entry.slug]))

    def test_blog_entry_edit_view_get(self):
        response = self.client.get(reverse('blog.entry.edit', args=[self.blog_entry.id, self.blog_entry.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-edit.html')

    def test_blog_entry_edit_view_post_invalid(self):
        response = self.client.post(reverse('blog.entry.edit', args=[self.blog_entry.id, self.blog_entry.slug]), {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog-entry-edit.html')

    def test_blog_entry_edit_view_post(self):
        response = self.client.post(reverse('blog.entry.edit', args=[self.blog_entry.id, self.blog_entry.slug]), {
            'title': 'This is a sample post title',
            'markdown': 'Sample post content goes here!',
            'html': '<p>Sample post content goes here!</p>',
        })
        self.assertRedirects(response, reverse('blog.entry.edit', args=[self.blog_entry.id, slugify('This is a sample post title')]))
