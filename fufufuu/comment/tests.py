from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from fufufuu.comment.forms import CommentForm
from fufufuu.comment.models import Comment
from fufufuu.core.tests import BaseTestCase


class CommentPostViewTests(BaseTestCase):

    def test_comment_post_view_get(self):
        response = self.client.get(reverse('comment.post'))
        self.assertRedirects(response, reverse('manga.list'))

    def test_comment_post_view_post_invalid(self):
        expected_count = Comment.objects.all().count()

        response = self.client.post(reverse('comment.post'))
        self.assertRedirects(response, reverse('manga.list'))

        actual_count = Comment.objects.all().count()
        self.assertEqual(expected_count, actual_count)

    def test_comment_post_view_post(self):
        redirect_url = reverse('manga', args=[self.manga.id, self.manga.slug])
        response = self.client.post(reverse('comment.post'), {
            'content_type': ContentType.objects.get_for_model(self.manga).id,
            'object_id': self.manga.id,
            'next': redirect_url,
            'markdown': 'This is a very simple comment.',
        })
        self.assertRedirects(response, redirect_url)

        comment = Comment.objects.get(markdown='This is a very simple comment.')
        self.assertEqual(comment.html, '<p>This is a very simple comment.</p>')
        self.assertEqual(comment.content_object, self.manga)
        self.assertEqual(comment.ip_address, '127.0.0.1')
        self.assertEqual(comment.created_by, self.user)


class CommentFormTests(BaseTestCase):

    def test_comment_form_init(self):
        form = CommentForm(self.manga)
        self.assertEqual(form.fields['content_type'].initial, ContentType.objects.get_for_model(self.manga).id)
        self.assertEqual(form.fields['object_id'].initial, self.manga.id)

    def test_comment_form_disallow_empty_comments(self):
        form = CommentForm(data={
            'content_type': ContentType.objects.get_for_model(self.manga).id,
            'object_id': self.manga.id,
            'markdown': '\n\n',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['markdown'], ['Your comment cannot be blank.'])

    def test_comment_form_save(self):
        content_type = ContentType.objects.get_for_model(self.manga)
        form = CommentForm(data={
            'content_type': content_type.id,
            'object_id': self.manga.id,
            'markdown': 'This is a very simple comment',
        })
        self.assertTrue(form.is_valid())

        self.request.META = {'REMOTE_ADDR': '127.0.0.1'}
        comment = form.save(self.request)

        self.assertEqual(comment.content_type, content_type)
        self.assertEqual(comment.object_id, self.manga.id)
        self.assertEqual(comment.ip_address, '127.0.0.1')
        self.assertEqual(comment.created_by, self.user)
        self.assertTrue(comment.created_on)
