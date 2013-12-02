from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from fufufuu.account.models import User


USERNAME_REGEX = r'^([a-zA-Z0-9]+_?)+[a-zA-Z0-9]$'


class AccountRegisterForm(forms.ModelForm):

    username = forms.RegexField(
        label=_('Username'),
        regex=USERNAME_REGEX,
        min_length=4,
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': _('Username'),
            'minlength': 4,
            'maxlength': 20,
        }),
        help_text=_('Your username must be 4 to 20 characters long and contain only letters, numbers and underscores.')
    )

    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Password'),
        })
    )

    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Confirm Password'),
        })
    )

    error_messages = {
        'duplicate_username': _('That username is already taken.'),
        'password_mismatch': _('The two password fields did not match.'),
    }

    class Meta:
        model = User
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
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


class AccountLoginForm(forms.Form):

    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Username'),
        })
    )

    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Password'),
        })
    )

    error_messages = {
        'invalid_login': _('Please enter a correct username and password. Note that both fields are case-sensitive.'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_cache = None

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
