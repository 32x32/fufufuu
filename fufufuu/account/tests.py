from django.core.urlresolvers import reverse
from fufufuu.account.models import User
from fufufuu.core.tests import BaseTestCase


class AccountLoginViewTests(BaseTestCase):

    def test_account_login_view_get_authenticated(self):
        response = self.client.get(reverse('account.login'))
        self.assertRedirects(response, reverse('manga.list'))

    def test_account_login_view_post_authenticated(self):
        response = self.client.post(reverse('account.login'))
        self.assertRedirects(response, reverse('manga.list'))

    def test_account_login_view_get(self):
        self.client.logout()
        response = self.client.get(reverse('account.login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-login.html')

    def test_account_login_view_post_invalid(self):
        self.client.logout()
        response = self.client.post(reverse('account.login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-login.html')

    def test_account_login_view_post(self):
        self.client.logout()
        response = self.client.post(reverse('account.login'), {
            'username': 'testuser',
            'password': 'password',
            'next': reverse('tag.list.author'),
        })
        self.assertRedirects(response, reverse('tag.list.author'))


class AccountRegisterViewTests(BaseTestCase):

    def test_account_register_view_get_authenticated(self):
        response = self.client.get(reverse('account.register'))
        self.assertRedirects(response, reverse('manga.list'))

    def test_account_register_view_post_authenticated(self):
        response = self.client.post(reverse('account.register'))
        self.assertRedirects(response, reverse('manga.list'))

    def test_account_register_view_get(self):
        self.client.logout()
        response = self.client.get(reverse('account.register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-register.html')

    def test_account_register_view_post_invalid(self):
        self.client.logout()
        response = self.client.post(reverse('account.register'), {
            'username': 'newuser',
            'password1': '1234',
            'password2': '5678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-register.html')

    def test_account_register_view_post(self):
        self.client.logout()
        response = self.client.post(reverse('account.register'), {
            'username': 'newuser',
            'password1': 'password',
            'password2': 'password',
            'next': reverse('tag.list.author'),
        })
        self.assertRedirects(response, reverse('tag.list.author'))

        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('password'))


class AccountLogoutViewTests(BaseTestCase):

    def test_account_logout_view_get(self):
        response = self.client.get(reverse('account.logout'))
        self.assertEqual(response.status_code, 405)

    def test_account_logout_view_post(self):
        response = self.client.post(reverse('account.logout'))
        self.assertRedirects(response, reverse('account.login'))
