from collections import defaultdict
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

    cover = forms.FileField(required=False, label=_('Cover'))

    tank = forms.CharField(required=False, label=_('Tank'))
    tank_chapter = forms.CharField(
        required=False,
        label=_('Chapter'),
        max_length=5,
        widget=forms.TextInput(attrs={
            'maxlength': '5',
        })
    )

    collection = forms.CharField(required=False, label=_('Collection'))
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

    TAG_LIMIT = 50

    class Meta:
        model = Manga
        fields = ('title', 'markdown', 'cover', 'category', 'language', 'uncensored')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.tags = []

        manga = kwargs['instance']
        self.collection_obj = manga.collection
        self.tank_obj = manga.tank
        self.initialize_tag_fields(manga)
        self.fields['cover'].required = bool(manga.cover)

    def initialize_tag_fields(self, manga):
        tag_list = manga.tags.all()
        tag_dict = defaultdict(list)
        for tag in tag_list:
            tag_dict[tag.tag_type].append(tag)
        self.fields['authors'].initial = ', '.join(tag_dict[TagType.AUTHOR])

    def clean_tags(self, tag_type, field_name):
        tags = self.cleaned_data.get(field_name)
        for name in tags.split(','):
            name = name.strip()[:50]
            if name: self.tags.append((tag_type, name))
        return tags

    def clean_tank(self):               return self.cleaned_data.get('tank').strip()
    def clean_tank_chapter(self):       return self.cleaned_data.get('tank_chapter').strip()
    def clean_collection(self):         return self.cleaned_data.get('collection').strip()
    def clean_collection_part(self):    return self.cleaned_data.get('collection_part').strip()

    def clean_authors(self):            return self.clean_tags(TagType.AUTHOR, 'authors')
    def clean_circles(self):            return self.clean_tags(TagType.AUTHOR, 'circles')
    def clean_content(self):            return self.clean_tags(TagType.AUTHOR, 'content')
    def clean_events(self):             return self.clean_tags(TagType.AUTHOR, 'events')
    def clean_magazines(self):          return self.clean_tags(TagType.AUTHOR, 'magazines')
    def clean_parodies(self):           return self.clean_tags(TagType.AUTHOR, 'parodies')
    def clean_scanlators(self):         return self.clean_tags(TagType.AUTHOR, 'scanlators')

    def clean(self):
        cd = self.cleaned_data
        if len(self.tags) > self.TAG_LIMIT:
            raise forms.ValidationError(_('Exceeded maximum number of allowed tags that can be assigned.'))

        tank = cd.get('tank')
        tank_chapter = cd.get('tank_chapter')

        if bool(tank) != bool(tank_chapter):
            raise forms.ValidationError(_('Please specify both tank and tank chapter.'))
        elif tank and tank_chapter:
            self.tank_obj = get_or_create_tag_data(TagType.TANK, cd.get('language'), tank)

        collection = cd.get('collection')
        collection_part = cd.get('collection_part')

        if bool(collection) != bool(collection_part):
            raise forms.ValidationError(_('Please specify both collection and collection part.'))
        elif collection and collection_part:
            self.collection_obj = get_or_create_tag_data(TagType.COLLECTION, cd.get('language'), collection)

        return cd

    def save_m2m(self, manga):
        tag_list = []
        for tag_type, name in self.tags:
            tag_data = get_or_create_tag_data(tag_type, Language.ENGLISH, name)
            while tag_data.alias: tag_data = tag_data.alias
            tag_list.append(tag_data.tag)
        manga.tags.add(*tag_list)

    def save(self):
        manga = super().save(commit=False)
        if self.tank_obj:
            manga.tank = self.tank_obj
            manga.tank_chapter = self.cleaned_data.get('tank_chapter')
        if self.collection_obj:
            manga.collection = self.collection_obj
            manga.collection_part = self.cleaned_data.get('collection_part')

        manga.save(updated_by=self.request.user)
        self.save_m2m(manga)
        return manga
