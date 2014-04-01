from captcha.fields import CaptchaField
from django import forms
from django.utils.translation import ugettext_lazy as _

from fufufuu.core.forms import BlankLabelSuffixMixin
from fufufuu.core.utils import get_ip_address

from fufufuu.report.enums import ReportMangaType
from fufufuu.report.models import ReportManga


class ReportMangaForm(BlankLabelSuffixMixin, forms.ModelForm):

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

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        if not self.request.user.is_authenticated():
            self.fields['captcha'] = CaptchaField()

    def save(self, manga, commit=True):
        report_manga = super().save(commit=False)
        report_manga.manga = manga
        report_manga.ip_address = get_ip_address(self.request)

        if self.request.user.is_authenticated():
            report_manga.created_by = self.request.user

        if commit:
            report_manga.save()

        return report_manga
