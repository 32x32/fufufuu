from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from fufufuu.account.models import User

from fufufuu.comment.forms import CommentForm
from fufufuu.comment.models import Comment
from fufufuu.comment.utils import attach_comment_count
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


class CommentDeleteViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.comment = Comment.objects.all()[0]

    def test_comment_delete_view_get(self):
        response = self.client.get(reverse('comment.delete', args=[self.comment.id]))
        self.assertRedirects(response, reverse('manga.list'))

    def test_comment_delete_view_post_owner(self):
        self.comment.created_by = self.user
        self.comment.save()

        response = self.client.post(reverse('comment.delete', args=[self.comment.id]))
        self.assertRedirects(response, reverse('manga.list'))
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_comment_delete_view_post_not_moderator(self):
        user = self.create_test_user('testuser2')
        self.comment.created_by = user
        self.comment.save()

        self.user.is_moderator = False
        self.user.save()

        response = self.client.post(reverse('comment.delete', args=[self.comment.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_comment_delete_view_post_moderator(self):
        user = self.create_test_user('testuser2')
        self.comment.created_by = user
        self.comment.save()

        response = self.client.post(reverse('comment.delete', args=[self.comment.id]))
        self.assertRedirects(response, reverse('manga.list'))
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())


class CommentFormTests(BaseTestCase):

    def test_comment_form_init(self):
        form = CommentForm(request=self.request, content_object=self.manga)
        self.assertEqual(form.fields['content_type'].initial, ContentType.objects.get_for_model(self.manga).id)
        self.assertEqual(form.fields['object_id'].initial, self.manga.id)

    def test_comment_form_disallow_empty_comments(self):
        form = CommentForm(request=self.request, data={
            'content_type': ContentType.objects.get_for_model(self.manga).id,
            'object_id': self.manga.id,
            'markdown': '\n\n',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['markdown'], ['Your comment cannot be blank.'])

    def test_comment_form_save(self):
        content_type = ContentType.objects.get_for_model(self.manga)
        form = CommentForm(request=self.request, data={
            'content_type': content_type.id,
            'object_id': self.manga.id,
            'markdown': 'This is a very simple comment',
        })
        self.assertTrue(form.is_valid())

        comment = form.save(self.request)

        self.assertEqual(comment.content_type, content_type)
        self.assertEqual(comment.object_id, self.manga.id)
        self.assertEqual(comment.ip_address, '127.0.0.1')
        self.assertEqual(comment.created_by, self.user)
        self.assertTrue(comment.created_on)

    def test_comment_form_user_comment_limit(self):
        content_type = ContentType.objects.get_for_model(self.manga)

        for i in range(self.user.comment_limit):
            Comment.objects.create(
                content_type=content_type,
                object_id=self.manga.id,
                markdown=i,
                html=i,
                created_by=self.user,
            )

        form = CommentForm(request=self.request, data={
            'content_type': content_type.id,
            'object_id': self.manga.id,
            'markdown': 'This is a very simple comment',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['markdown'], ['Sorry, you have reached your comment limit for the day.'])


class CommentUtilTests(BaseTestCase):

    def test_attach_comment_count_empty(self):
        user1 = self.user
        user2 = self.create_test_user('user2')
        user3 = self.create_test_user('user3')

        attach_comment_count([user1, user2, user3])

        self.assertEqual(user1.comment_count, 0)
        self.assertEqual(user2.comment_count, 0)
        self.assertEqual(user3.comment_count, 0)

    def test_attach_comment_count(self):
        user1 = self.user
        user2 = self.create_test_user('user2')
        user3 = self.create_test_user('user3')

        content_type = ContentType.objects.get_for_model(User)
        Comment.objects.create(content_type=content_type, object_id=user1.id, markdown='test', html='test', created_by=self.user)
        Comment.objects.create(content_type=content_type, object_id=user3.id, markdown='test', html='test', created_by=self.user)
        Comment.objects.create(content_type=content_type, object_id=user3.id, markdown='test', html='test', created_by=self.user)

        attach_comment_count([user1, user2, user3])

        self.assertEqual(user1.comment_count, 1)
        self.assertEqual(user2.comment_count, 0)
        self.assertEqual(user3.comment_count, 2)
