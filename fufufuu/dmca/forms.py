from django import forms
from django.utils.translation import ugettext_lazy as _
from fufufuu.account.models import User
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.utils import convert_markdown
from fufufuu.dmca.models import DmcaAccount, DmcaRequest
from fufufuu.manga.enums import MangaStatus


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


class DmcaRequestForm(BlankLabelSuffixMixin, forms.ModelForm):

    comment = forms.CharField(
        required=False,
        label=_('(Optional) Provide any additional notes or comments'),
        widget=forms.Textarea(attrs={
            'rows': '5',
        })
    )

    check1 = forms.BooleanField(
        label=_('I have a good faith belief that use of the copyrighted materials described above as allegedly infringing is not authorized by the copyright owner, its agent, or the law.'),
        initial=True,
    )

    check2 = forms.BooleanField(
        label=_('The information in this notification is accurate, and I swear, under penalty of perjury, that I am the copyright owner or am authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.'),
        initial=True,
    )

    class Meta:
        model = DmcaRequest
        fields = ['comment']

    def __init__(self, manga, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manga = manga
        self.request = request

    def save(self):
        dmca_request = super().save(commit=False)
        dmca_request.dmca_account = self.request.user.dmca_account
        dmca_request.manga = self.manga
        dmca_request.save()

        self.manga.status = MangaStatus.DMCA
        self.manga.save(updated_by=self.request.user)

        return dmca_request
