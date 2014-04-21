from django import forms
from django.utils.translation import ugettext as _, ugettext
from fufufuu.account.models import User
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.utils import convert_markdown
from fufufuu.dmca.models import DmcaAccount


class DmcaAccountForm(forms.ModelForm):

    markdown = forms.CharField(
        label=_('Description'),
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={
            'maxlength': '5000',
            'rows': '6'
        }),
        help_text=_('<a href="/f/markdown/" class="text-xsmall" target="_blank">This field uses markdown for formatting.</a>')
    )

    class Meta:
        model = DmcaAccount
        fields = ['name', 'email', 'website', 'markdown']

    def clean_markdown(self):
        markdown = self.cleaned_data.get('markdown')
        self.html = convert_markdown(markdown)
        return markdown

    def save(self):
        dmca_account = super().save(commit=False)
        if self.html:
            dmca_account.html = self.html
        dmca_account.save()
        return dmca_account


class DmcaAccountCreateForm(BlankLabelSuffixMixin, forms.Form):

    username = forms.CharField(
        max_length=30,
        error_messages={
            'required': _('You must specify a username to add.'),
        }
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            self.target_user = User.objects.get(username=username)
            if self.target_user.dmca_account:
                raise forms.ValidationError(_('The user "{}" already has a DMCA account.').format(username))
        except User.DoesNotExist:
            raise forms.ValidationError(_('The user "{}" does not exist.').format(username))
        return username

    def save(self):
        self.target_user.dmca_account = DmcaAccount.objects.create(
            name='Corporation Name',
            email='example@corporation.com',
            website='http://corporation.com'
        )
        self.target_user.save()
        return self.target_user
