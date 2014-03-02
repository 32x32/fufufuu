from captcha.conf import settings
from captcha.models import CaptchaStore
from django.core.files.uploadedfile import SimpleUploadedFile
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
        challenge, response = settings.get_challenge()()
        store = CaptchaStore.objects.create(challenge=challenge, response=response)

        self.client.logout()
        response = self.client.post(reverse('account.register'), {
            'username': 'newuser',
            'password1': 'password',
            'password2': 'password',
            'next': reverse('tag.list.author'),
            'captcha_0': store.hashkey,
            'captcha_1': store.response,
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


class AccountSettingsViewTests(BaseTestCase):

    def test_account_settings_view_get(self):
        response = self.client.get(reverse('account.settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-settings.html')

    def test_account_settings_view_post(self):
        self.assertEqual(self.user.markdown, '')
        self.assertEqual(self.user.html, '')
        self.assertFalse(self.user.avatar)

        response = self.client.post(reverse('account.settings'), {
            'markdown': 'This is some markdown.',
            'avatar': SimpleUploadedFile('test.jpg', self.create_test_image_file().getvalue())
        })
        self.assertRedirects(response, reverse('account.settings'))

        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.markdown, 'This is some markdown.')
        self.assertEqual(user.html, '<p>This is some markdown.</p>\n')
        self.assertTrue(user.avatar)

    def test_account_settings_view_post_clear_avatar(self):
        self.user.avatar = SimpleUploadedFile('test.jpg', self.create_test_image_file().getvalue())
        self.user.save()

        self.assertTrue(self.user.avatar)

        response = self.client.post(reverse('account.settings'), {
            'avatar-clear': 'on'
        })
        self.assertRedirects(response, reverse('account.settings'))

        user = User.objects.get(id=self.user.id)
        self.assertFalse(user.avatar)


class AccountSettingsPasswordViewTests(BaseTestCase):

    def test_account_settings_password_view_get(self):
        response = self.client.get(reverse('account.settings.password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-settings.html')

    def test_account_settings_password_view_post_password_mismatch(self):
        response = self.client.post(reverse('account.settings.password'), {
            'old_password': 'password',
            'new_password1': '1234',
            'new_password2': '5678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-settings.html')

    def test_account_settings_password_view_post_incorrect_old_password(self):
        response = self.client.post(reverse('account.settings.password'), {
            'old_password': '1234',
            'new_password1': '5678',
            'new_password2': '5678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-settings.html')

    def test_account_settings_password_view_post(self):
        response = self.client.post(reverse('account.settings.password'), {
            'old_password': 'password',
            'new_password1': '1234',
            'new_password2': '1234',
        })
        self.assertRedirects(response, reverse('account.settings'))

        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password('1234'))
