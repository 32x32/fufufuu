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
        help_text=_('Please do not include [Circle], (Author) or other tag-related information in the title. Use the tags section below for this information.'),
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

    authors = forms.CharField(
        required=False,
        label=_('Authors'),
    )
    circles = forms.CharField(
        required=False,
        label=_('Circles'),
    )
    content = forms.CharField(
        required=False,
        label=_('Content'),
    )
    events = forms.CharField(
        required=False,
        label=_('Events'),
    )
    magazines = forms.CharField(
        required=False,
        label=_('Magazines'),
    )
    parodies = forms.CharField(
        required=False,
        label=_('Parodies'),
    )
    scanlators = forms.CharField(
        required=False,
        label=_('Scanlators'),
    )

    category = forms.ChoiceField(label=_('Category'), choices=MangaCategory.choices)
    language = forms.ChoiceField(label=_('Language'), choices=Language.choices)
    uncensored = forms.BooleanField(label=_('Uncensored'))

    class Meta:
        model = Manga
        fields = ('title', 'markdown', 'cover', 'category', 'language', 'uncensored')
