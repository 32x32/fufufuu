from django import forms
from django.utils.translation import ugettext as _

from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.models import SiteSetting


class SiteSettingForm(BlankLabelSuffixMixin, forms.Form):

    announcement = forms.CharField(
        label=_('Announcement'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '2',
            'class': 'space-bottom-0',
        })
    )

    enable_comments = forms.BooleanField(
        label=_('Enable Comments'),
        required=False,
    )

    enable_registration = forms.BooleanField(
        label=_('Enable Registration'),
        required=False
    )

    enable_uploads = forms.BooleanField(
        label=_('Enable Uploads'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'data' not in kwargs:
            self.initialize_data()

    def initialize_data(self):
        settings_dict = SiteSetting.as_dict()
        for k, v in settings_dict.items():
            self.fields[k.lower()].initial = v

    def save_setting(self, key, user):
        val = self.cleaned_data.get(key.lower())
        SiteSetting.set_val(key, val, user)

    def save(self, user):
        for key in SiteSettingKey.choices_dict.keys():
            self.save_setting(key, user)
        SiteSetting.clear_cache()
