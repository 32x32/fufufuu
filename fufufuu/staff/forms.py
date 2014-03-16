from django import forms
from django.core.cache import cache
from django.utils.translation import ugettext as _
from fufufuu.core.enums import SiteSettingKey
from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.models import SiteSetting, SITE_SETTING_CACHE_KEY


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
        try:
            site_setting = SiteSetting.objects.get(key=key)
            site_setting.val = val
            site_setting.updated_by = user
            site_setting.save()
        except SiteSetting.DoesNotExist:
            SiteSetting.objects.create(
                key=key,
                val=val,
                updated_by=user
            )

    def save(self, user):
        for key in SiteSettingKey.choices_dict.keys():
            self.save_setting(key, user)
        cache.delete(SITE_SETTING_CACHE_KEY)
