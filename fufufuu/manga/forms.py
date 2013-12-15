from django import forms
from django.utils.translation import ugettext as _
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.languages import Language
from fufufuu.manga.enums import MangaCategory
from fufufuu.manga.models import Manga


class MangaEditForm(BlankLabelSuffixMixin, forms.ModelForm):

    title = forms.CharField(
        label=_('Title'),
        max_length=100,
        widget=forms.TextInput(attrs={
            'required': 'required',
            'maxlength': '100',
        })
    )

    markdown = forms.CharField(
        label=_('Description'),
        max_length=5000,
        widget=forms.Textarea(attrs={
            'maxlength': '5000',
            'rows': '6'
        })
    )

    cover = forms.FileField(
        label=_('Cover'),
    )

    category = forms.ChoiceField(
        label=_('Category'),
        choices=MangaCategory.choices,
    )

    language = forms.ChoiceField(
        label=_('Language'),
        choices=Language.choices,
    )

    uncensored = forms.BooleanField(
        label=_('Uncensored'),
    )

    class Meta:
        model = Manga
        fields = ('title', 'markdown', 'cover', 'category', 'language', 'uncensored')
