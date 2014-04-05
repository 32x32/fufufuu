from django import forms
from django.forms.models import BaseModelFormSet
from django.utils.translation import ugettext_lazy as _
from fufufuu.report.enums import ReportStatus
from fufufuu.report.models import ReportManga, ReportMangaResolution


class ModeratorReportMangaForm(forms.ModelForm):

    class Meta:
        model = ReportManga
        fields = ['quality']


class ModeratorReportMangaFormSet(BaseModelFormSet):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        action = self.data.get('action')
        if action not in ['remove', 'keep']:
            raise forms.ValidationError(_('No action has been selected for the manga.'))

    def save(self):
        remove = self.data.get('action') == 'remove'
        resolution = ReportMangaResolution.objects.create(
            removed=remove,
            comment=self.data.get('comment'),
            created_by=self.user,
        )
        for form in self.forms:
            instance = form.instance
            instance.resolution = resolution
            instance.status = ReportStatus.CLOSED
            instance.save()

        return resolution
