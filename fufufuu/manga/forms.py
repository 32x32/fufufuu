from collections import defaultdict

from captcha.fields import CaptchaField
from django import forms
from django.db.models.aggregates import Sum
from django.forms.models import BaseModelFormSet
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.languages import Language
from fufufuu.core.utils import convert_markdown, get_ip_address, send_email_alert, validate_image
from fufufuu.image.enums import ImageKeyType
from fufufuu.image.filters import image_resize
from fufufuu.manga.enums import MangaCategory, MangaAction, MangaStatus, MANGA_FIELDNAME_MAP
from fufufuu.manga.models import Manga, MangaPage
from fufufuu.manga.utils import MangaArchiveGenerator
from fufufuu.report.enums import ReportMangaType
from fufufuu.report.models import ReportManga
from fufufuu.tag.enums import TagType
from fufufuu.tag.utils import get_or_create_tag_by_name_or_alias


class MangaEditForm(BlankLabelSuffixMixin, forms.ModelForm):

    title = forms.CharField(
        label=MANGA_FIELDNAME_MAP['title'],
        max_length=100,
        help_text=_('Please do not include [Circle], (Author) or other tag-related information in the title. Use the tags section for this information.'),
        widget=forms.TextInput(attrs={
            'required': 'required',
            'maxlength': '100',
        })
    )

    markdown = forms.CharField(
        label=MANGA_FIELDNAME_MAP['markdown'],
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={
            'maxlength': '1000',
            'rows': '6'
        }),
        help_text=_('Use the description to add a link to your blog or website! <a href="/f/markdown/" class="text-xsmall" target="_blank">This field uses markdown for formatting.</a>')
    )

    cover = forms.FileField(
        required=False,
        label=MANGA_FIELDNAME_MAP['cover'],
        widget=forms.FileInput(),
    )

    tank = forms.CharField(required=False, label=MANGA_FIELDNAME_MAP['tank'])
    tank_chapter = forms.CharField(
        required=False,
        label=MANGA_FIELDNAME_MAP['tank_chapter'],
        max_length=5,
        widget=forms.TextInput(attrs={
            'maxlength': '5',
        })
    )

    collection = forms.CharField(required=False, label=MANGA_FIELDNAME_MAP['collection'])
    collection_part = forms.CharField(
        required=False,
        label=MANGA_FIELDNAME_MAP['collection_part'],
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

    category = forms.ChoiceField(label=MANGA_FIELDNAME_MAP['category'], choices=MangaCategory.choices)
    language = forms.ChoiceField(label=MANGA_FIELDNAME_MAP['language'], choices=Language.choices)
    uncensored = forms.BooleanField(label=MANGA_FIELDNAME_MAP['uncensored'], required=False)

    action = forms.ChoiceField(choices=MangaAction.choices)

    TAG_LIMIT = 50

    class Meta:
        model = Manga
        fields = ('title', 'markdown', 'cover', 'category', 'language', 'uncensored')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []
        self.request = request
        self.tags = []
        self.collection_obj = None
        self.tank_obj = None
        self.html = None

        if 'instance' not in kwargs:
            raise RuntimeError('MangaEditForm must be used with an existing Manga instance.')

        manga = kwargs['instance']
        self.fields['cover'].required = bool(manga.cover)

        if 'data' not in kwargs:
            self.initialize_tag_fields(manga)
            self.fields['tank'].initial             = manga.tank_id and manga.tank.name or ''
            self.fields['tank_chapter'].initial     = manga.tank_chapter
            self.fields['collection'].initial       = manga.collection_id and manga.collection.name or ''
            self.fields['collection_part'].initial  = manga.collection_part

    def initialize_tag_fields(self, manga):
        tag_list = manga.tags.all()
        tag_dict = defaultdict(list)
        for tag in tag_list: tag_dict[tag.tag_type].append(tag.name)

        self.fields['authors'].initial      = ', '.join(sorted(tag_dict[TagType.AUTHOR]))
        self.fields['circles'].initial      = ', '.join(sorted(tag_dict[TagType.CIRCLE]))
        self.fields['content'].initial      = ', '.join(sorted(tag_dict[TagType.CONTENT]))
        self.fields['events'].initial       = ', '.join(sorted(tag_dict[TagType.EVENT]))
        self.fields['magazines'].initial    = ', '.join(sorted(tag_dict[TagType.MAGAZINE]))
        self.fields['parodies'].initial     = ', '.join(sorted(tag_dict[TagType.PARODY]))
        self.fields['scanlators'].initial   = ', '.join(sorted(tag_dict[TagType.SCANLATOR]))

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
    def clean_circles(self):            return self.clean_tags(TagType.CIRCLE, 'circles')
    def clean_content(self):            return self.clean_tags(TagType.CONTENT, 'content')
    def clean_events(self):             return self.clean_tags(TagType.EVENT, 'events')
    def clean_magazines(self):          return self.clean_tags(TagType.MAGAZINE, 'magazines')
    def clean_parodies(self):           return self.clean_tags(TagType.PARODY, 'parodies')
    def clean_scanlators(self):         return self.clean_tags(TagType.SCANLATOR, 'scanlators')

    def clean_action(self):
        action = self.cleaned_data.get('action')
        if action == MangaAction.PUBLISH:
            if self.instance.status == MangaStatus.DRAFT:
                if self.instance.mangapage_set.count() < 1:
                    raise forms.ValidationError(_('Please upload at least one image before publishing.'))
            else:
                raise forms.ValidationError(_('This upload cannot be published.'))
        return action

    def clean_markdown(self):
        markdown = self.cleaned_data.get('markdown')
        self.html = convert_markdown(markdown)
        return markdown

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if cover:
            validate_image(cover)
        return cover

    def clean(self):
        cd = self.cleaned_data
        if len(self.tags) > self.TAG_LIMIT:
            raise forms.ValidationError(_('Exceeded maximum number of allowed tags that can be assigned.'))

        tank_name = cd.get('tank')
        tank_chapter = cd.get('tank_chapter')

        if bool(tank_name) != bool(tank_chapter):
            raise forms.ValidationError(_('Please specify both tank and tank chapter (or leave them both blank).'))

        collection_name = cd.get('collection')
        collection_part = cd.get('collection_part')

        if bool(collection_name) != bool(collection_part):
            raise forms.ValidationError(_('Please specify both collection and collection part (or leave them both blank).'))

        return cd

    def get_tag_list(self):
        tag_list = []
        for tag_type, name in self.tags:
            tag = get_or_create_tag_by_name_or_alias(tag_type, name, self.request.user)
            if tag.name != name:
                self.messages.append(_('{} has been replaced with {}'.format(name, tag.name)))
            tag_list.append(tag)
        return tag_list

    def save(self):
        manga = super().save(commit=False)

        cd = self.cleaned_data

        tank_name, tank_chapter = cd.get('tank'), cd.get('tank_chapter')
        if tank_name and tank_chapter:
            manga.tank = get_or_create_tag_by_name_or_alias(TagType.TANK, tank_name, self.request.user)
            manga.tank_chapter = tank_chapter
        else:
            manga.tank = None
            manga.tank_chapter = None

        collection_name, collection_part = cd.get('collection'), cd.get('collection_part')
        if collection_name and collection_part:
            manga.collection = get_or_create_tag_by_name_or_alias(TagType.COLLECTION, collection_name, self.request.user)
            manga.collection_part = collection_part
        else:
            manga.collection = None
            manga.collection_part = None

        if self.html:
            manga.html = self.html

        if cd.get('action') == MangaAction.PUBLISH:
            manga.status = MangaStatus.PUBLISHED
            manga.published_on = timezone.now()
            send_email_alert(
                subject='[Fufufuu] Published: {}'.format(manga.title),
                message=manga.info_text,
            )

        manga.save(self.request.user)
        manga.tags.clear()
        manga.tags.add(*self.get_tag_list())

        if manga.status == MangaStatus.PUBLISHED:
            MangaArchiveGenerator.generate(manga)

        if manga.tank and not manga.tank.cover:
            manga.tank.set_default_cover()
        if manga.collection and not manga.collection.cover:
            manga.collection.set_default_cover()

        return manga


class MangaPageForm(forms.ModelForm):

    select = forms.BooleanField(
        label=_('Select'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'mp-select'})
    )

    class Meta:
        model = MangaPage
        fields = []


class MangaPageFormSet(BaseModelFormSet):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.messages = []

        for form in self:
            mp = form.instance
            mp.image_thumbnail_url = image_resize(mp.image, ImageKeyType.MANGA_THUMB, mp.id)

    @property
    def unselected_forms(self):
        if hasattr(self, '_unselected_forms'):
            return self._unselected_forms

        def _unselected(form): return not form.cleaned_data.get('select')
        self._unselected_forms = list(filter(_unselected, self.ordered_forms))
        return self._unselected_forms

    @property
    def selected_forms(self):
        if hasattr(self, '_selected_forms'):
            return self._selected_forms

        def _selected(form): return form.cleaned_data.get('select')
        self._selected_forms = list(filter(_selected, self.ordered_forms))
        return self._selected_forms

    def clean(self):
        action = self.data.get('action')
        if action not in ['reorder', 'set_cover', 'delete']:
            raise forms.ValidationError(_('The form was submitted without an action, please re-submit this form.'))

        if action == 'set_cover':
            if len(self.selected_forms) != 1:
                raise forms.ValidationError(_('Please select only a single image to set as the cover.'))
        elif action == 'delete':
            if len(self.unselected_forms) == 0:
                raise forms.ValidationError(_('Please leave at least one image in this upload undeleted.'))
            elif len(self.selected_forms) == 0:
                raise forms.ValidationError(_('Please select at least one image to delete.'))

    def save(self, manga):
        getattr(self, self.data.get('action'))()
        if manga.status == MangaStatus.PUBLISHED:
            MangaArchiveGenerator.generate(manga)

    def reorder(self):
        for page, form in enumerate(self.ordered_forms, start=1):
            form.instance.page = page
            form.instance.save()
        self.messages.append(('success', _('The image order has been updated.')))

    def set_cover(self):
        form = self.selected_forms[0]
        manga = form.instance.manga
        manga.cover = form.instance.image.file
        manga.save(self.user)
        self.messages.append(('success', _('The selected image has been set as cover.')))

    def delete(self):
        for form in self.selected_forms:
            form.instance.delete()
        for page, form in enumerate(self.unselected_forms, start=1):
            form.instance.page = page
            form.instance.save()
        self.messages.append(('error', _('The selected images have been deleted.')))


class MangaListFilterForm(forms.Form):

    non_h           = forms.BooleanField(required=False)
    ecchi           = forms.BooleanField(required=False)
    vanilla         = forms.BooleanField(required=False)
    alternative     = forms.BooleanField(required=False)
    yaoi            = forms.BooleanField(required=False)
    yuri            = forms.BooleanField(required=False)
    other           = forms.BooleanField(required=False)

    lang            = forms.ChoiceField(choices=Language.choices, required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def save(self):
        cd = self.cleaned_data
        self.request.session['manga_list_filters'] = {
            'non_h':        bool(cd.get('non_h')),
            'ecchi':        bool(cd.get('ecchi')),
            'vanilla':      bool(cd.get('vanilla')),
            'alternative':  bool(cd.get('alternative')),
            'yaoi':         bool(cd.get('yaoi')),
            'yuri':         bool(cd.get('yuri')),
            'other':        bool(cd.get('other')),
            'lang':         cd.get('lang'),
        }


class MangaReportForm(BlankLabelSuffixMixin, forms.ModelForm):

    ANONYMOUS_USER_REPORT_WEIGHT = 5
    PENDING_WEIGHT = 50

    type = forms.ChoiceField(
        label=_('Select the reason for reporting'),
        choices=ReportMangaType.choices,
        widget=forms.RadioSelect(),
    )

    comment = forms.CharField(
        label=_('Provide any additional details for the report'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '3',
            'maxlength': '300',
        }),
        max_length=300,
    )

    check = forms.BooleanField(
        label=_('I am petitioning to remove this gallery based on the information I provided above.')
    )

    class Meta:
        model = ReportManga
        fields = ('type', 'comment',)

    def __init__(self, request, manga, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.manga = manga

        if not self.request.user.is_authenticated():
            self.fields['captcha'] = CaptchaField()

    def clean(self):
        cd = self.cleaned_data
        user = self.request.user
        if user.is_authenticated() and ReportManga.open.filter(manga=self.manga, created_by=user).exists():
            raise forms.ValidationError(_('You have already reported this manga.'))
        return cd

    def save(self):
        report_manga = super().save(commit=False)
        report_manga.manga = self.manga
        report_manga.ip_address = get_ip_address(self.request)

        if self.request.user.is_authenticated():
            report_manga.created_by = self.request.user
            report_manga.weight = self.request.user.report_weight
        else:
            report_manga.weight = self.ANONYMOUS_USER_REPORT_WEIGHT

        report_manga.save()

        total_weight = ReportManga.open.filter(manga=self.manga).aggregate(total_weight=Sum('weight')).get('total_weight', 0)
        if total_weight >= self.PENDING_WEIGHT:
            self.manga.status = MangaStatus.PENDING
            self.manga.save(self.manga.updated_by)

        send_email_alert(
            subject='[Fufufuu] Reported: {}'.format(self.manga.title),
            message=report_manga.email_text,
        )

        return report_manga
