from captcha.conf import settings
from captcha.models import CaptchaStore
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from fufufuu.account.forms import AccountRegisterForm, AccountSettingsForm, AccountLoginForm

from fufufuu.account.models import User
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.models import SiteSetting
from fufufuu.core.tests import BaseTestCase
from fufufuu.dmca.models import DmcaAccount
from fufufuu.settings import MAX_IMAGE_FILE_SIZE


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
        SiteSetting.set_val(SiteSettingKey.ENABLE_REGISTRATION, 'True', self.user)

        self.client.logout()
        response = self.client.post(reverse('account.register'), {
            'username': 'newuser',
            'password1': '1234',
            'password2': '5678',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-register.html')

    def test_account_register_view_post_disabled(self):
        SiteSetting.set_val(SiteSettingKey.ENABLE_REGISTRATION, 'False', self.user)
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

        self.assertRedirects(response, reverse('account.register'))

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
        self.assertEqual(user.html, '<p>This is some markdown.</p>')
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


class AccountSettingsDmcaViewTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user.dmca_account = DmcaAccount.objects.create(
            name='Corporation Name',
            email='example@corporation.com',
            website='http://corporation.com'
        )
        self.user.save()

    def test_account_settings_dmca_view_get_no_account(self):
        self.user.dmca_account.delete()

        response = self.client.get(reverse('account.settings.dmca'))
        self.assertEqual(response.status_code, 404)

    def test_account_settings_dmca_view_get(self):
        response = self.client.get(reverse('account.settings.dmca'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-settings-dmca.html')

    def test_account_settings_dmca_view_post_no_account(self):
        self.user.dmca_account.delete()

        response = self.client.post(reverse('account.settings.dmca'))
        self.assertEqual(response.status_code, 404)

    def test_account_settings_dmca_view_post_invalid(self):
        response = self.client.post(reverse('account.settings.dmca'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/account-settings-dmca.html')

    def test_account_settings_dmca_view_post(self):
        url = reverse('account.settings.dmca')
        response = self.client.post(url, {
            'name': 'Sample Corporation',
            'email': 'sample@corporation.com',
            'website': 'http://sample-corporation.com',
            'markdown': 'Here is some markdown!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        dmca_account = User.objects.get(id=self.user.id).dmca_account
        self.assertEqual(dmca_account.name, 'Sample Corporation')
        self.assertEqual(dmca_account.email, 'sample@corporation.com')
        self.assertEqual(dmca_account.website, 'http://sample-corporation.com')
        self.assertEqual(dmca_account.markdown, 'Here is some markdown!')
        self.assertEqual(dmca_account.html, '<p>Here is some markdown!</p>')


class AccountSettingsFormTests(BaseTestCase):

    def test_account_settings_form_avatar_filesize_too_large(self):
        form = AccountSettingsForm(instance=self.user, files={
            'avatar': SimpleUploadedFile('test.jpg', b'0' * (MAX_IMAGE_FILE_SIZE+1)),
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['avatar'], ['test.jpg is over 10MB in size.'])

    def test_account_settings_form_avatar_not_an_image(self):
        form = AccountSettingsForm(instance=self.user, files={
            'avatar': SimpleUploadedFile('test.jpg', b'0'),
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['avatar'], ['test.jpg failed to verify as an image file.'])

    def test_account_settings_form_avatar_dimensions_too_large(self):
        form = AccountSettingsForm(instance=self.user, files={
            'avatar': SimpleUploadedFile('test.jpg', self.create_test_image_file(width=8001).getvalue()),
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['avatar'], ['test.jpg is larger than 8000x8000 pixels.'])

    def test_account_settings_form(self):
        form = AccountSettingsForm(instance=self.user, files={
            'avatar': SimpleUploadedFile('test.jpg', self.create_test_image_file().getvalue()),
        })
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertTrue(user.avatar)


class AccountRegisterFormTests(BaseTestCase):

    def test_valid_usernames(self):
        username_list = [
            'abcd',
            'ab_cd',
            'ab_cd_ef',
            'abcdefghijklmnopqrst'
        ]
        for username in username_list:
            form = AccountRegisterForm(data={'username': username})
            form.is_valid()
            self.assertFalse('username' in form.errors)

    def test_invalid_usernames(self):
        username_list = [
            'abc',
            '_bdc',
            'abc_',
            'a__d',
            'abcdefghijklmnopqrstu',
            'ab-cd',
            '中文',
        ]
        for username in username_list:
            form = AccountRegisterForm(data={'username': username})
            form.is_valid()
            self.assertTrue('username' in form.errors)


class AccountLoginFormTests(BaseTestCase):

    def test_account_login_form(self):
        form = AccountLoginForm(request=self.request, data={
            'username': 'testuser',
            'password': 'password',
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_account_login_form_fail(self):
        for i in range(AccountLoginForm.LOGIN_ATTEMPT_LIMIT):
            form = AccountLoginForm(request=self.request, data={
                'username': 'testuser',
                'password': 'wrong-password',
            })
            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors['__all__'], [AccountLoginForm.error_messages['invalid_login']])

        form = AccountLoginForm(request=self.request, data={
            'username': 'testuser',
            'password': 'password',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['captcha'], ['This field is required.'])

        challenge, response = settings.get_challenge()()
        store = CaptchaStore.objects.create(challenge=challenge, response=response)

        form = AccountLoginForm(request=self.request, data={
            'username': 'testuser',
            'password': 'password',
            'captcha_0': store.hashkey,
            'captcha_1': store.response,
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)
