from django import forms
from django.utils.translation import ugettext_lazy as _

from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.models import SiteSetting


class SiteSettingForm(BlankLabelSuffixMixin, forms.Form):

    announcement = forms.CharField(
        label=_('Announcement'),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': '2',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        key_list = sorted(SiteSettingKey.form_field_type.keys())

        for key in key_list:
            field_cls = SiteSettingKey.form_field_type[key]
            key = key.lower()
            if key in self.fields:
                continue
            self.fields[key] = field_cls(label=SiteSettingKey.choices_dict.get(key), required=False)

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
