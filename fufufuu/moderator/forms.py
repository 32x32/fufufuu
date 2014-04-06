from django import forms
from django.forms.models import BaseModelFormSet
from django.utils.translation import ugettext_lazy as _
from fufufuu.manga.enums import MangaStatus
from fufufuu.report.enums import ReportStatus
from fufufuu.report.models import ReportManga, ReportMangaResolution


class ModeratorReportMangaForm(forms.ModelForm):

    class Meta:
        model = ReportManga
        fields = ['quality']


class ModeratorReportMangaFormSet(BaseModelFormSet):

    def clean(self):
        action = self.data.get('action')
        if action not in ['remove', 'keep']:
            raise forms.ValidationError(_('No action has been selected for the manga.'))

    def save(self, user, manga):
        remove = self.data.get('action') == 'remove'

        if remove:
            manga.status = MangaStatus.REMOVED
            manga.save(updated_by=user)

        resolution = ReportMangaResolution.objects.create(
            manga=manga,
            removed=remove,
            comment=self.data.get('comment'),
            created_by=user,
        )
        for form in self.forms:
            instance = form.instance
            instance.resolution = resolution
            instance.status = ReportStatus.CLOSED
            instance.save()

        return resolution
