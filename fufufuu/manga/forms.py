from django import forms
from django.utils.translation import ugettext as _
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.languages import Language
from fufufuu.manga.enums import MangaCategory
from fufufuu.manga.models import Manga
from fufufuu.tag.enums import TagType


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
        required=False,
        max_length=5000,
        widget=forms.Textarea(attrs={
            'maxlength': '5000',
            'rows': '6'
        })
    )

    cover = forms.FileField(
        required=False,
        label=_('Cover'),
    )

    tank = forms.CharField(
        required=False,
        label=_('Tank'),
    )
    tank_chapter = forms.CharField(
        required=False,
        label=_('Chapter'),
        max_length=5,
        widget=forms.TextInput(attrs={
            'maxlength': '5',
        })
    )

    collection = forms.CharField(
        required=False,
        label=_('Collection'),
    )
    collection_part = forms.CharField(
        required=False,
        label=_('Part'),
        max_length=5,
        widget=forms.TextInput(attrs={
            'maxlength': '5',
        })
    )

    authors = forms.CharField(required=False, label=_('Authors'))
    circles = forms.CharField(required=False, label=_('Circles'))
    content = forms.CharField(required=False, label=_('Content'))
    events = forms.CharField(required=False, label=_('Events'))
    magazines = forms.CharField(required=False, label=_('Magazines'))
    parodies = forms.CharField(required=False, label=_('Parodies'))
    scanlators = forms.CharField(required=False, label=_('Scanlators'))

    category = forms.ChoiceField(label=_('Category'), choices=MangaCategory.choices)
    language = forms.ChoiceField(label=_('Language'), choices=Language.choices)
    uncensored = forms.BooleanField(required=False, label=_('Uncensored'))

    class Meta:
        model = Manga
        fields = ('title', 'markdown', 'cover', 'category', 'language', 'uncensored')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_tags(self, tag_type, field_name):
        tags = self.cleaned_data.get(field_name)
        for name in tags.split(','):
            name = name.strip()[:50]
            if name: self.tags.append((tag_type, name))
        return tags

    def clean_authors(self):    return self.clean_tags(TagType.AUTHOR, 'authors')
    def clean_circles(self):    return self.clean_tags(TagType.AUTHOR, 'circles')
    def clean_content(self):    return self.clean_tags(TagType.AUTHOR, 'content')
    def clean_events(self):     return self.clean_tags(TagType.AUTHOR, 'events')
    def clean_magazines(self):  return self.clean_tags(TagType.AUTHOR, 'magazines')
    def clean_parodies(self):   return self.clean_tags(TagType.AUTHOR, 'parodies')
    def clean_scanlators(self): return self.clean_tags(TagType.AUTHOR, 'scanlators')

    def clean(self):
        cd = self.cleaned_data
        # handle tank and collection
        return cd

    def save(self):
        manga = super().save(commit=False)
        manga.save(updated_by=self.request.user)

        # update tank and collection
        # process m2m information

        return manga
