from captcha.fields import CaptchaField
from django import forms
from fufufuu.report.enums import ReportMangaType

from fufufuu.report.models import ReportManga


class ReportMangaForm(forms.ModelForm):

    type = forms.ChoiceField(
        choices=ReportMangaType.choices,
        widget=forms.RadioSelect(),
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(),
        max_length=300,
    )

    class Meta:
        model = ReportManga
        fields = ('type', 'comment',)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if not self.user.is_authenticated():
            self.fields['captcha'] = CaptchaField()

    def save(self, manga, commit=True):
        report_manga = super().save(commit=False)
        report_manga.manga = manga

        if self.user.is_authenticated():
            report_manga.created_by = self.user

        if commit:
            report_manga.save()

        return report_manga
