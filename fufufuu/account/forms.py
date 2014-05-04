from captcha.fields import CaptchaField
from django import forms
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from fufufuu.account.models import User
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.utils import convert_markdown, validate_image, get_ip_address


USERNAME_REGEX = r'^\w{4,20}$'


class AccountRegisterForm(BlankLabelSuffixMixin, forms.ModelForm):

    username = forms.RegexField(
        label=_('Username'),
        regex=USERNAME_REGEX,
        min_length=4,
        max_length=20,
        widget=forms.TextInput(attrs={
            'autofocus': 'autofocus',
            'required': 'required',
            'minlength': 4,
            'maxlength': 20,
        }),
        help_text=_('Your username must be 4 to 20 characters long and contain only letters, numbers and underscores.')
    )

    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'required': 'required',
        }),
    )

    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'required': 'required',
        }),
    )

    captcha = CaptchaField()

    error_messages = {
        'duplicate_username': _('That username is already taken.'),
        'password_mismatch': _('The two password fields did not match.'),
    }

    class Meta:
        model = User
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '_' == username[0] or '_' == username[-1]:
            raise forms.ValidationError(_('A username cannot start or end with an underscore.'))
        if '__' in username:
            raise forms.ValidationError(_('Consecutive underscores are no allowed in usernames.'))
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(self.error_messages['duplicate_username'])
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

    def save(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password2')

        user = super().save(commit=False)
        user.set_password(password)
        user.save()

        self.user_cache = authenticate(username=username, password=password)
        return self.user_cache


class AccountLoginForm(BlankLabelSuffixMixin, forms.Form):

    LOGIN_KEY = 'login-limit-{ip_address}'
    LOGIN_TIMEOUT = 3 * 60 # 3 minute
    LOGIN_ATTEMPT_LIMIT = 5

    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(attrs={
            'autofocus': 'autofocus',
            'required': 'required',
        }),
    )

    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'required': 'required',
        }),
    )

    error_messages = {
        'invalid_login': _('Please enter a correct username and password. Note that both fields are case-sensitive.'),
    }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

        key = self.get_cache_key()
        if cache.get(key, 0) >= self.LOGIN_ATTEMPT_LIMIT:
            self.fields['captcha'] = CaptchaField()

    def get_cache_key(self):
        return self.LOGIN_KEY.format(ip_address=get_ip_address(self.request))

    def update_attempt(self):
        key = self.get_cache_key()
        if cache.get(key) is None:
            cache.set(key, 1, self.LOGIN_TIMEOUT)
        else:
            cache.incr(key)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                self.update_attempt()
                raise forms.ValidationError(self.error_messages['invalid_login'])

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class AccountSettingsForm(BlankLabelSuffixMixin, forms.ModelForm):

    avatar = forms.FileField(
        required=False,
        label=_('Avatar'),
        widget=forms.FileInput(),
    )

    markdown = forms.CharField(
        label=_('Description'),
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={
            'maxlength': '1000',
            'rows': '6'
        }),
        help_text=_('Use the description to add a link to your blog or website! <a href="/f/markdown/" class="text-xsmall" target="_blank">This field uses markdown for formatting.</a>')
    )

    class Meta:
        model = User
        fields = ['markdown', 'avatar']

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs:
            raise RuntimeError('This form must be used with a User instance.')

        super().__init__(*args, **kwargs)
        self.html = None

    def clean_markdown(self):
        markdown = self.cleaned_data.get('markdown')
        self.html = convert_markdown(markdown)
        return markdown

    def clean_avatar(self):
        if 'avatar-clear' in self.data:
            return False
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            validate_image(avatar)
        return avatar

    def save(self):
        user = super().save(commit=False)
        if self.html:
            user.html = self.html
        user.save()
        return user


class AccountSettingsPasswordForm(BlankLabelSuffixMixin, forms.Form):

    old_password = forms.CharField(
        label=_('Current Password'),
        widget=forms.PasswordInput(attrs={'required': 'required'})
    )

    new_password1 = forms.CharField(
        label=_('New Password'),
        widget=forms.PasswordInput(attrs={'required': 'required'})
    )

    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        widget=forms.PasswordInput(attrs={'required': 'required'})
    )

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_incorrect': _('Your current password was entered incorrectly. Please enter it again.'),
    }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(self.error_messages['password_incorrect'])
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
